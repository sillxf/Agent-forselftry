"""Compatible facade coordinating ingestion, indexing, snapshots and query pipelines."""
from functools import partial
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version as package_version
from pathlib import Path
import sqlite3
from threading import RLock

from app.config import (
    RAG_BM25_TOP_K, RAG_CHILD_MAX_TOKENS, RAG_CHILD_OVERLAP_TOKENS,
    RAG_DENSE_TOP_K, RAG_EMBEDDING_MODEL, RAG_KNOWLEDGE_DIR, RAG_OCR_ENABLED,
    RAG_PARENT_MAX_TOKENS, RAG_STORAGE_DIR, RAG_RETRIEVAL_STRATEGY,
    RAG_RERANKER_MODEL, RAG_CONTEXT_CHAR_BUDGET, RAG_RERANKER_TIMEOUT_SECONDS,
    RAG_EMBEDDING_CACHE_REVISION,
)
from app.rag.chunking.child_chunker import ChildChunker
from app.rag.chunking.parent_chunker import ParentChunker
from app.rag.embedder import embed_texts, get_model
from app.rag.indexing.vector_store import FaissVectorStore, VectorStoreInterface
from app.rag.indexing.pipeline import IndexingPipeline
from app.rag.indexing.build_service import BuildService
from app.rag.indexing.embedding_cache import CachedEmbedder
from app.rag.indexing.snapshot_repository import SnapshotRepository
from app.rag.ingestion.docling_parser import DoclingParser, file_checksum
from app.rag.ingestion.pipeline import IngestionPipeline, IngestionResult
from app.rag.loader import discover_documents
from app.rag.lifecycle.registry import DocumentRegistry
from app.rag.lifecycle.service import LifecycleService
from app.rag.retrieval.pipeline import RetrievalPipeline
from app.rag.retrieval.policy import RetrievalPolicy
from app.rag.retrieval.orchestrator import RetrievalOrchestrator


class KnowledgeRetriever:
    INDEX_VERSION = 7

    def __init__(
        self, build=True, *, knowledge_dir=None, storage_dir=None, parser=None,
        tokenizer=None, embedding_fn=None, model_name=RAG_EMBEDDING_MODEL,
        parent_max_tokens=RAG_PARENT_MAX_TOKENS, child_max_tokens=RAG_CHILD_MAX_TOKENS,
        overlap_tokens=RAG_CHILD_OVERLAP_TOKENS, dense_top_k=RAG_DENSE_TOP_K,
        bm25_top_k=RAG_BM25_TOP_K, store_factory=FaissVectorStore,
        cache_enabled=True, embedding_cache_revision=RAG_EMBEDDING_CACHE_REVISION,
        retrieval_policy=None, reranker_factory=None,
    ):
        self.knowledge_dir = Path(knowledge_dir) if knowledge_dir is not None else RAG_KNOWLEDGE_DIR
        self.storage_dir = Path(storage_dir) if storage_dir is not None else RAG_STORAGE_DIR
        self.model_name = model_name
        self._configured_model_name = model_name
        self.tokenizer = tokenizer
        self.embedding_fn = embedding_fn
        self.parent_max_tokens, self.child_max_tokens = parent_max_tokens, child_max_tokens
        self.overlap_tokens = overlap_tokens
        self.dense_top_k, self.bm25_top_k = dense_top_k, bm25_top_k
        self.parser = parser if parser is not None else DoclingParser(
            archive_dir=self.storage_dir / "parsed", image_dir=self.storage_dir / "images",
            ocr_enabled=RAG_OCR_ENABLED,
        )
        self.registry = DocumentRegistry(self.storage_dir)
        self.lifecycle = LifecycleService(self.storage_dir, self.registry)
        self.store_factory = store_factory
        self.cache_enabled = cache_enabled
        self.embedding_cache_revision = embedding_cache_revision
        self.last_build_metrics = {}
        self.repository = SnapshotRepository(self.storage_dir, store_factory=store_factory)
        self.store: VectorStoreInterface | None = None
        self.parents = {}
        self.documents = []
        self._pipeline = None
        self._lock = RLock()
        self._generation_id = None
        self._follow_current = False
        self._publishing = False
        self._failed_generation = None
        self._executor = None
        self._build_future = None
        self.last_build_error = None
        self.last_refresh_error = None
        self.build_service = BuildService(self)
        policy = retrieval_policy or RetrievalPolicy(
            default_strategy=RAG_RETRIEVAL_STRATEGY, reranker_model=RAG_RERANKER_MODEL,
            max_context_chars=RAG_CONTEXT_CHAR_BUDGET, reranker_timeout_seconds=RAG_RERANKER_TIMEOUT_SECONDS)
        self.orchestrator = RetrievalOrchestrator(policy, reranker_factory=reranker_factory)
        if build:
            self._ensure_index()

    def _signature(self):
        files = discover_documents(self.knowledge_dir)
        return {
            "version": self.INDEX_VERSION, "model": self._configured_model_name,
            "lifecycle_revision": self.registry.revision,
            "embedding_cache_revision": self.embedding_cache_revision,
            "parent_tokens": self.parent_max_tokens, "child_tokens": self.child_max_tokens,
            "overlap": self.overlap_tokens, "ocr": self.parser.ocr_enabled,
            "processing": {
                "revision": 2,
                "parser": f"{type(self.parser).__module__}.{type(self.parser).__qualname__}",
                "docling": package_version("docling"), "transformers": package_version("transformers"),
                "tokenizer": (f"{type(self.tokenizer).__module__}.{type(self.tokenizer).__qualname__}"
                              if self.tokenizer is not None else "embedding-model-tokenizer"),
                "tokenizer_name": str(getattr(self.tokenizer, "name_or_path", "")),
            },
            "files": [{"path": str(path.resolve()), "checksum": file_checksum(path)} for path in files],
        }, files

    def _embed(self):
        return self.embedding_fn or partial(embed_texts, model_name=self._configured_model_name)

    @staticmethod
    def _view_options(snapshot):
        return {} if snapshot.view_store is None else dict(
            view_store=snapshot.view_store, view_model_name=snapshot.view_model_name)

    def _bind_live_filter(self, pipeline, documents):
        if any(document.version_id for document in documents):
            self.registry.eligible_ids(document.document_id for document in documents if document.version_id)

        def eligible():
            mapping = {}
            for document in documents:
                if document.version_id:
                    mapping[document.document_id] = document.document_id
                elif not self.registry.path.exists():
                    mapping[document.document_id] = None
                else:
                    registered = self.registry.lookup_path(document.source_path)
                    if registered is None:
                        raise ValueError("Legacy source cannot be resolved in the managed registry; rebuild before serving")
                    mapping[document.document_id] = registered.document_id
            allowed = self.registry.eligible_ids(value for value in mapping.values() if value is not None)
            return {key for key, value in mapping.items() if value is None or value in allowed}
        pipeline.eligibility = eligible

    def _load_runtime(self, snapshot, pointer):
        model_name = pointer["signature"]["model"]
        parents = {parent.parent_id: parent for parent in snapshot.parents}
        pipeline = self._prepare_pipeline(snapshot.store, parents, model_name, **self._view_options(snapshot))
        self._bind_live_filter(pipeline, snapshot.documents)
        pipeline.generation_id = pointer["generation"]
        self._activate_index(snapshot.store, snapshot.documents, parents, pipeline, model_name)
        self._generation_id, self._follow_current = pointer["generation"], True

    def _refresh(self):
        if not self._follow_current or self._publishing:
            return
        try:
            pointer = self.repository.current_pointer()
            if pointer is None or pointer["generation"] in {self._generation_id, self._failed_generation}:
                return
            snapshot = self.repository.load_generation(pointer["generation"], expected_signature=pointer["signature"])
            self._load_runtime(snapshot, pointer)
            self._failed_generation = None
            self.last_refresh_error = None
        except (OSError, ValueError, KeyError, sqlite3.DatabaseError) as exc:
            self.last_refresh_error = str(exc)
            if "pointer" in locals() and pointer is not None:
                self._failed_generation = pointer.get("generation")

    def _ensure_index(self):
        with self._lock:
            if self.store is not None:
                self._refresh()
                return
            try:
                published = self.repository.load_published()
            except (OSError, ValueError) as exc:
                self.last_refresh_error = str(exc)
                published = None
            if published is not None:
                snapshot, pointer = published
                self._load_runtime(snapshot, pointer)
                if pointer.get("rollback"):
                    return
        self.build_service.recover()
        # A last-known published runtime is already visible to other threads here.
        try:
            signature, _ = self._signature()
            if published is None or signature != pointer["signature"]:
                self.build_index()
        except Exception as exc:
            self.last_build_error = str(exc)
            if self.store is None:
                raise

    def build_index(self):
        """Synchronous explicit build; old queries continue on their pinned pipeline."""
        return self.build_service.run()

    def build_index_async(self):
        """One in-process background request, plus a cross-process single-writer lock."""
        with self._lock:
            if self._build_future is not None and not self._build_future.done():
                return self._build_future
            if self._executor is None:
                self._executor = ThreadPoolExecutor(max_workers=1, thread_name_prefix="rag-build")
            self._build_future = self._executor.submit(self.build_index)
            return self._build_future

    def _assemble_snapshot(self, signature, files):
        entries = {str(path.resolve()): item for path, item in zip(files, signature["files"], strict=True)}
        for path in files:
            existing = self.registry.lookup_path(path)
            if existing is None or existing.deleted_at is None:
                self.lifecycle.import_document(path, expected_hash=entries[str(path.resolve())]["checksum"])
        sources, revision = self.registry.capture_sources(files)
        signature = dict(signature, lifecycle_revision=revision)
        result = IngestionResult()
        if sources:
            tokenizer, child_budget = self.tokenizer, self.child_max_tokens
            if tokenizer is None:
                model = get_model(signature["model"])
                tokenizer = model.tokenizer
                special = tokenizer.num_special_tokens_to_add(pair=False)
                child_budget = min(child_budget, model.max_seq_length - special)
            parent_chunker = ParentChunker(tokenizer, self.parent_max_tokens)
            child_chunker = ChildChunker(tokenizer, child_budget, min(self.overlap_tokens, child_budget - 1))
            ingestion = IngestionPipeline(self.parser, parent_chunker, child_chunker,
                                          cache_dir=self.storage_dir / "artifacts" if self.cache_enabled else None)
            processing = {key: value for key, value in signature.items() if key not in {"files", "lifecycle_revision", "embedding_cache_revision"}}
            processing["effective_child_tokens"] = child_budget
            for document, version in sources:
                if version.content_hash != entries[str(Path(document.source_path).resolve())]["checksum"]:
                    raise ValueError("Source version changed while freezing build inputs")
            documents = [self.lifecycle.processing_document(document, version, processing) for document, version in sources]
            result = ingestion.run(self.knowledge_dir, documents=documents)
        embed = self._embed()
        cached_embed = None
        if self.cache_enabled:
            cached_embed = CachedEmbedder(embed, self.storage_dir / "embedding_cache", {
                "model": signature["model"], "cache_revision": self.embedding_cache_revision,
                "sentence_transformers": package_version("sentence-transformers"),
                "transformers": package_version("transformers"),
            })
            embed = cached_embed
        snapshot = IndexingPipeline(embed, store_factory=self.store_factory).build(result)
        if cached_embed is not None:
            snapshot.embedding_cache_keys = [cached_embed.key(item["search_text"]) for item in snapshot.store.records]
        self.last_build_metrics = {
            "artifact_cache_hits": ingestion.cache_hits if sources else 0,
            "parsed_documents": ingestion.cache_misses if sources else 0,
            "embedding_cache_hits": cached_embed.hits if cached_embed else 0,
            "encoded_texts": cached_embed.encoded if cached_embed else len(result.children),
        }
        return snapshot, signature

    def build_view_index(self, views):
        return self.build_service.run(views=views)

    def rollback_generation(self, generation):
        return self.build_service.rollback(generation)

    def _publish_snapshot(self, snapshot, signature, *, job_id, expected_generation):
        saved = self.repository.save(snapshot, signature)
        self.registry.update_job_output(job_id, signature["lifecycle_revision"], saved.generation)
        parents = {parent.parent_id: parent for parent in snapshot.parents}
        pipeline = self._prepare_pipeline(snapshot.store, parents, signature["model"], **self._view_options(snapshot))
        self._bind_live_filter(pipeline, snapshot.documents)
        pipeline.generation_id = saved.generation
        with self.registry.publication_guard(signature["lifecycle_revision"]), self._lock:
            if self.build_service._generation() != expected_generation:
                raise RuntimeError("Stale build: current generation changed")
            self._publishing = True
            try:
                self.repository.publish(saved)
                self._activate_index(snapshot.store, snapshot.documents, parents, pipeline, signature["model"])
                self._generation_id, self._follow_current = saved.generation, True
                self._failed_generation = None
            finally:
                self._publishing = False

    @property
    def pipeline(self):
        """Each caller pins one complete runtime; the next request can follow a new pointer."""
        self._ensure_index()
        with self._lock:
            return self._pipeline

    def attach_index(self, store, documents, parents, *, model_name=None, view_store=None, view_model_name=None):
        """Explicit frozen/offline attachment; live lifecycle management is not applied."""
        with self._lock:
            model_name = model_name if model_name is not None else self.model_name
            pipeline = self._prepare_pipeline(store, parents, model_name,
                                              view_store=view_store, view_model_name=view_model_name)
            self._activate_index(store, documents, parents, pipeline, model_name)
            self._follow_current, self._generation_id = False, None

    def _prepare_pipeline(self, store, parents, model_name, *, view_store=None, view_model_name=None):
        if view_store is not None and view_model_name != model_name:
            raise ValueError("View index and original index must use the same embedding model")
        return RetrievalPipeline.from_index(
            store, parents, embed=self.embedding_fn or partial(embed_texts, model_name=model_name),
            dense_top_k=self.dense_top_k, bm25_top_k=self.bm25_top_k, view_store=view_store,
        )

    def _activate_index(self, store, documents, parents, pipeline, model_name):
        """Install prepared references under the facade lock; no construction or I/O."""
        self.store, self.documents, self.parents = store, documents, parents
        self.model_name, self._pipeline = model_name, pipeline

    def search_rankings(self, query: str, k: int = 5, strategy: str = "hybrid", *, candidate_k=None, reranker=None):
        """Compatible Child and unique-Parent rankings from the composed pipeline."""
        if not query.strip() or k <= 0:
            return {"children": [], "parents": [], "candidate_count": 0}
        pipeline = self.pipeline
        return pipeline.search_rankings(query, k, strategy, candidate_k=candidate_k, reranker=reranker)

    @property
    def retrieval_modes(self):
        return ("hybrid", "multi_view") if self.pipeline.multi_view_dense is not None else ("hybrid",)

    def search(self, query: str, k: int = 2, *, retrieval_mode: str = "hybrid"):
        if retrieval_mode != "hybrid":
            # Kept for explicit offline/HTTP experiments, never advertised to the Agent.
            return self.search_rankings(query, k, retrieval_mode)["parents"]
        return self.search_with_trace(query, k)["results"]

    def search_with_trace(self, query, k=5):
        return self.orchestrator.search(self, query, k)

"""Compatible facade coordinating ingestion, indexing, snapshots and query pipelines."""

from functools import partial
from contextlib import nullcontext
from concurrent.futures import ThreadPoolExecutor
from importlib.metadata import version as package_version
from pathlib import Path
import sqlite3
import json
from uuid import uuid4
from threading import RLock

from rag_service.core.config import (
    RAG_BM25_TOP_K,
    RAG_CHILD_MAX_TOKENS,
    RAG_CHILD_OVERLAP_TOKENS,
    RAG_DENSE_TOP_K,
    RAG_EMBEDDING_MODEL,
    RAG_KNOWLEDGE_DIR,
    RAG_OCR_ENABLED,
    RAG_PARENT_MAX_TOKENS,
    RAG_STORAGE_DIR,
    RAG_RETRIEVAL_STRATEGY,
    RAG_RERANKER_MODEL,
    RAG_CONTEXT_CHAR_BUDGET,
    RAG_RERANKER_TIMEOUT_SECONDS,
    RAG_EMBEDDING_CACHE_REVISION,
)
from rag_service.core.embedder import embed_texts
from rag_service.core.indexing.vector_store import (
    FaissVectorStore,
    VectorStoreInterface,
)
from rag_service.core.indexing.build_service import BuildService
from rag_service.core.indexing.snapshot_repository import SnapshotRepository
from rag_service.core.ingestion.docling_parser import DoclingParser, file_checksum
from rag_service.core.loader import discover_documents
from rag_service.core.lifecycle.registry import DocumentRegistry
from rag_service.core.lifecycle.service import LifecycleService
from rag_service.core.retrieval.pipeline import RetrievalPipeline
from rag_service.core.retrieval.policy import RetrievalPolicy
from rag_service.core.retrieval.orchestrator import RetrievalOrchestrator


class KnowledgeRetriever:
    INDEX_VERSION = 8

    def __init__(
        self,
        build=True,
        *,
        knowledge_dir=None,
        storage_dir=None,
        parser=None,
        tokenizer=None,
        embedding_fn=None,
        model_name=RAG_EMBEDDING_MODEL,
        parent_max_tokens=RAG_PARENT_MAX_TOKENS,
        child_max_tokens=RAG_CHILD_MAX_TOKENS,
        overlap_tokens=RAG_CHILD_OVERLAP_TOKENS,
        dense_top_k=RAG_DENSE_TOP_K,
        bm25_top_k=RAG_BM25_TOP_K,
        store_factory=FaissVectorStore,
        cache_enabled=True,
        embedding_cache_revision=RAG_EMBEDDING_CACHE_REVISION,
        retrieval_policy=None,
        reranker_factory=None,
        view_llm_factory=None,
        auto_build=True,
        embedding_resolver=None,
    ):
        self.auto_build = auto_build
        self.knowledge_dir = (
            Path(knowledge_dir) if knowledge_dir is not None else RAG_KNOWLEDGE_DIR
        )
        self.storage_dir = (
            Path(storage_dir) if storage_dir is not None else RAG_STORAGE_DIR
        )
        self.model_name = model_name
        self._configured_model_name = model_name
        self.tokenizer = tokenizer
        self.embedding_fn = embedding_fn
        self.embedding_resolver = embedding_resolver
        self.progress = lambda stage: None
        self.publication_guard = nullcontext
        self.parent_max_tokens, self.child_max_tokens = (
            parent_max_tokens,
            child_max_tokens,
        )
        self.overlap_tokens = overlap_tokens
        self.dense_top_k, self.bm25_top_k = dense_top_k, bm25_top_k
        self.parser = (
            parser
            if parser is not None
            else DoclingParser(
                archive_dir=self.storage_dir / "parsed",
                image_dir=self.storage_dir / "images",
                ocr_enabled=RAG_OCR_ENABLED,
            )
        )
        self.registry = DocumentRegistry(self.storage_dir)
        self.lifecycle = LifecycleService(self.storage_dir, self.registry)
        self.store_factory = store_factory
        self.cache_enabled = cache_enabled
        self.embedding_cache_revision = embedding_cache_revision
        self.last_build_metrics = {}
        self.repository = SnapshotRepository(
            self.storage_dir, store_factory=store_factory
        )
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
        from rag_service.core.view_generation import ViewGenerationService

        self.view_service = ViewGenerationService(self, llm_factory=view_llm_factory)
        policy = retrieval_policy or RetrievalPolicy(
            default_strategy=RAG_RETRIEVAL_STRATEGY,
            reranker_model=RAG_RERANKER_MODEL,
            max_context_chars=RAG_CONTEXT_CHAR_BUDGET,
            reranker_timeout_seconds=RAG_RERANKER_TIMEOUT_SECONDS,
        )
        self._policy_path = self.storage_dir / "retrieval_policy.json"
        self._policy_override = retrieval_policy is not None
        self._policy_stamp = None
        self.orchestrator = RetrievalOrchestrator(
            policy, reranker_factory=reranker_factory
        )
        self.refresh_policy()
        if build:
            self._ensure_index()

    def _signature(self):
        files = [
            p
            for p in discover_documents(self.knowledge_dir)
            if not self.registry.is_blocked(p)
        ]
        known = {str(p.resolve()) for p in files}
        for document in self.registry.list_documents():
            path = Path(document.source_path)
            if (
                not document.deleted_at
                and not document.purged_at
                and (
                    document.selected_version_id
                    or not path.resolve().is_relative_to(self.knowledge_dir.resolve())
                )
            ):
                if not path.is_file() and not document.selected_version_id:
                    raise ValueError(
                        "An explicitly registered external source is missing"
                    )
                if str(path.resolve()) not in known:
                    files.append(path)
                    known.add(str(path.resolve()))
        files.sort(key=lambda p: str(p.resolve()).lower())

        def checksum(path):
            if path.is_file():
                return file_checksum(path)
            document = self.registry.lookup_path(path)
            versions = self.registry.list_versions(document.document_id)
            return next(
                v.content_hash
                for v in versions
                if v.version_id == document.selected_version_id
            )

        return {
            "version": self.INDEX_VERSION,
            "model": self._configured_model_name,
            "lifecycle_revision": self.registry.revision,
            "embedding_cache_revision": self.embedding_cache_revision,
            "parent_tokens": self.parent_max_tokens,
            "child_tokens": self.child_max_tokens,
            "overlap": self.overlap_tokens,
            "ocr": self.parser.ocr_enabled,
            "processing": {
                "revision": 2,
                "parser": f"{type(self.parser).__module__}.{type(self.parser).__qualname__}",
                "docling": package_version("docling"),
                "transformers": package_version("transformers"),
                "tokenizer": (
                    f"{type(self.tokenizer).__module__}.{type(self.tokenizer).__qualname__}"
                    if self.tokenizer is not None
                    else "embedding-model-tokenizer"
                ),
                "tokenizer_name": str(getattr(self.tokenizer, "name_or_path", "")),
            },
            "files": [
                {"path": str(path.resolve()), "checksum": checksum(path)}
                for path in files
            ],
        }, files

    def _embed(self):
        return (
            self.embedding_resolver(self._configured_model_name).embed_documents
            if self.embedding_resolver
            else self.embedding_fn
            or partial(embed_texts, model_name=self._configured_model_name)
        )

    @staticmethod
    def _view_options(snapshot):
        return dict(
            view_store=snapshot.view_store,
            view_model_name=snapshot.view_model_name,
            sparse=snapshot.sparse,
        )

    def _bind_live_filter(self, pipeline, documents):
        if any(document.version_id for document in documents):
            self.registry.eligible_ids(
                document.document_id for document in documents if document.version_id
            )

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
                        raise ValueError(
                            "Legacy source cannot be resolved in the managed registry; rebuild before serving"
                        )
                    mapping[document.document_id] = registered.document_id
            allowed = self.registry.eligible_ids(
                value for value in mapping.values() if value is not None
            )
            return {
                key
                for key, value in mapping.items()
                if value is None or value in allowed
            }

        pipeline.eligibility = eligible

    def _load_runtime(self, snapshot, pointer):
        model_name = pointer["signature"]["model"]
        parents = {parent.parent_id: parent for parent in snapshot.parents}
        pipeline = self._prepare_pipeline(
            snapshot.store, parents, model_name, **self._view_options(snapshot)
        )
        self._bind_live_filter(pipeline, snapshot.documents)
        pipeline.generation_id = pointer["generation"]
        self._activate_index(
            snapshot.store, snapshot.documents, parents, pipeline, model_name
        )
        self._generation_id, self._follow_current = pointer["generation"], True

    def _refresh(self):
        if not self._follow_current or self._publishing:
            return
        try:
            pointer = self.repository.current_pointer()
            if pointer is None or pointer["generation"] in {
                self._generation_id,
                self._failed_generation,
            }:
                return
            snapshot = self.repository.load_generation(
                pointer["generation"], expected_signature=pointer["signature"]
            )
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
        if not self.auto_build:
            if self.store is None:
                raise ValueError(
                    "No published knowledge index; explicitly build or migrate it first"
                )
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

    def build_index(self, *, full=False):
        """Synchronous explicit build; old queries continue on their pinned pipeline."""
        return self.build_service.run(full=full)

    def build_index_async(self, *, full=False):
        """One in-process background request, plus a cross-process single-writer lock."""
        with self._lock:
            if self._build_future is not None and not self._build_future.done():
                return self._build_future
            if self._executor is None:
                self._executor = ThreadPoolExecutor(
                    max_workers=1, thread_name_prefix="rag-build"
                )
            self._build_future = self._executor.submit(self.build_index, full=full)

            def completed(future):
                error = future.exception()
                if error is not None:
                    self.last_build_error = str(error)

            self._build_future.add_done_callback(completed)
            return self._build_future

    def build_view_index(self, views):
        return self.build_service.run(views=views)

    def rollback_generation(self, generation):
        return self.build_service.rollback(generation)

    def _publish_snapshot(self, snapshot, signature, *, job_id, expected_generation):
        saved = self.repository.save(snapshot, signature)
        self.registry.update_job_output(
            job_id, signature["lifecycle_revision"], saved.generation
        )
        parents = {parent.parent_id: parent for parent in snapshot.parents}
        pipeline = self._prepare_pipeline(
            snapshot.store, parents, signature["model"], **self._view_options(snapshot)
        )
        self._bind_live_filter(pipeline, snapshot.documents)
        pipeline.generation_id = saved.generation
        with (
            self.publication_guard(),
            self.registry.publication_guard(signature["lifecycle_revision"]),
            self._lock,
        ):
            if self.build_service._generation() != expected_generation:
                raise RuntimeError("Stale build: current generation changed")
            self._publishing = True
            try:
                self.repository.publish(saved)
                self._activate_index(
                    snapshot.store,
                    snapshot.documents,
                    parents,
                    pipeline,
                    signature["model"],
                )
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

    def attach_index(
        self,
        store,
        documents,
        parents,
        *,
        model_name=None,
        view_store=None,
        view_model_name=None,
    ):
        """Explicit frozen/offline attachment; live lifecycle management is not applied."""
        with self._lock:
            model_name = model_name if model_name is not None else self.model_name
            pipeline = self._prepare_pipeline(
                store,
                parents,
                model_name,
                view_store=view_store,
                view_model_name=view_model_name,
            )
            self._activate_index(store, documents, parents, pipeline, model_name)
            self._follow_current, self._generation_id = False, None

    def _prepare_pipeline(
        self,
        store,
        parents,
        model_name,
        *,
        view_store=None,
        view_model_name=None,
        sparse=None,
    ):
        if view_store is not None and view_model_name != model_name:
            raise ValueError(
                "View index and original index must use the same embedding model"
            )
        return RetrievalPipeline.from_index(
            store,
            parents,
            embed=(
                self.embedding_resolver(model_name).embed_query
                if self.embedding_resolver
                else self.embedding_fn or partial(embed_texts, model_name=model_name)
            ),
            dense_top_k=self.dense_top_k,
            bm25_top_k=self.bm25_top_k,
            view_store=view_store,
            sparse=sparse,
        )

    def _activate_index(self, store, documents, parents, pipeline, model_name):
        """Install prepared references under the facade lock; no construction or I/O."""
        self.store, self.documents, self.parents = store, documents, parents
        self.model_name, self._pipeline = model_name, pipeline

    def search_rankings(
        self,
        query: str,
        k: int = 5,
        strategy: str = "hybrid",
        *,
        candidate_k=None,
        reranker=None,
    ):
        """Compatible Child and unique-Parent rankings from the composed pipeline."""
        if not query.strip() or k <= 0:
            return {"children": [], "parents": [], "candidate_count": 0}
        pipeline = self.pipeline
        return pipeline.search_rankings(
            query, k, strategy, candidate_k=candidate_k, reranker=reranker
        )

    @property
    def retrieval_modes(self):
        return (
            ("hybrid", "multi_view")
            if self.pipeline.multi_view_dense is not None
            else ("hybrid",)
        )

    def search(self, query: str, k: int = 2, *, retrieval_mode: str = "hybrid"):
        if retrieval_mode != "hybrid":
            # Kept for explicit offline/HTTP experiments, never advertised to the Agent.
            return self.search_rankings(query, k, retrieval_mode)["parents"]
        return self.search_with_trace(query, k)["results"]

    def search_with_trace(self, query, k=5, *, supplement=False, as_of=None):
        self.refresh_policy()
        if as_of is not None:
            from rag_service.core.lifecycle.versions import HistoricalRetriever

            snapshot, publication = self.repository.at(as_of)
            historical = HistoricalRetriever(self, snapshot, publication, as_of)
            return self.orchestrator.search(historical, query, k, supplement=supplement)
        return self.orchestrator.search(self, query, k, supplement=supplement)

    def restore_version(self, document_id, version_id):
        from rag_service.core.lifecycle.versions import restore_version

        return restore_version(self, document_id, version_id)

    def purge_document(self, document_id):
        from rag_service.core.lifecycle.purge import purge_document

        return purge_document(self, document_id)

    def refresh_policy(self):
        if self._policy_override or not self._policy_path.exists():
            return
        stamp = self._policy_path.stat().st_mtime_ns
        if stamp != self._policy_stamp:
            self.orchestrator.policy = RetrievalPolicy.model_validate_json(
                self._policy_path.read_text(encoding="utf-8")
            )
            self._policy_stamp = stamp

    def set_policy(self, policy):
        policy = RetrievalPolicy.model_validate(policy)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        temporary = self.storage_dir / (".policy-" + uuid4().hex + ".tmp")
        try:
            temporary.write_text(policy.model_dump_json(indent=2), encoding="utf-8")
            temporary.replace(self._policy_path)
        finally:
            temporary.unlink(missing_ok=True)
        self.orchestrator.policy = policy
        self._policy_stamp = self._policy_path.stat().st_mtime_ns
        self._policy_override = False
        return policy

"""Compatible facade coordinating ingestion, indexing, snapshots and query pipelines."""
from functools import partial
from pathlib import Path
from threading import RLock

from app.config import (
    RAG_BM25_TOP_K, RAG_CHILD_MAX_TOKENS, RAG_CHILD_OVERLAP_TOKENS,
    RAG_DENSE_TOP_K, RAG_EMBEDDING_MODEL, RAG_KNOWLEDGE_DIR, RAG_OCR_ENABLED,
    RAG_PARENT_MAX_TOKENS, RAG_STORAGE_DIR,
)
from app.rag.chunking.child_chunker import ChildChunker
from app.rag.chunking.parent_chunker import ParentChunker
from app.rag.embedder import embed_texts, get_model
from app.rag.indexing.vector_store import FaissVectorStore, VectorStoreInterface
from app.rag.indexing.pipeline import IndexingPipeline
from app.rag.indexing.snapshot_repository import SnapshotRepository
from app.rag.ingestion.docling_parser import DoclingParser, file_checksum
from app.rag.ingestion.pipeline import IngestionPipeline, IngestionResult
from app.rag.loader import discover_documents
from app.rag.retrieval.pipeline import RetrievalPipeline


class KnowledgeRetriever:
    INDEX_VERSION = 5

    def __init__(
        self, build=True, *, knowledge_dir=None, storage_dir=None, parser=None,
        tokenizer=None, embedding_fn=None, model_name=RAG_EMBEDDING_MODEL,
        parent_max_tokens=RAG_PARENT_MAX_TOKENS, child_max_tokens=RAG_CHILD_MAX_TOKENS,
        overlap_tokens=RAG_CHILD_OVERLAP_TOKENS, dense_top_k=RAG_DENSE_TOP_K,
        bm25_top_k=RAG_BM25_TOP_K, store_factory=FaissVectorStore,
    ):
        self.knowledge_dir = Path(knowledge_dir) if knowledge_dir is not None else RAG_KNOWLEDGE_DIR
        self.storage_dir = Path(storage_dir) if storage_dir is not None else RAG_STORAGE_DIR
        self.model_name = model_name
        self.tokenizer = tokenizer
        self.embedding_fn = embedding_fn
        self.parent_max_tokens, self.child_max_tokens = parent_max_tokens, child_max_tokens
        self.overlap_tokens = overlap_tokens
        self.dense_top_k, self.bm25_top_k = dense_top_k, bm25_top_k
        self.parser = parser if parser is not None else DoclingParser(
            archive_dir=self.storage_dir / "parsed", image_dir=self.storage_dir / "images",
            ocr_enabled=RAG_OCR_ENABLED,
        )
        self.store_factory = store_factory
        self.repository = SnapshotRepository(self.storage_dir, store_factory=store_factory)
        self.store: VectorStoreInterface | None = None
        self.parents = {}
        self.documents = []
        self._pipeline = None
        self._lock = RLock()
        if build:
            self._ensure_index()

    def _signature(self):
        files = discover_documents(self.knowledge_dir)
        return {
            "version": self.INDEX_VERSION, "model": self.model_name,
            "parent_tokens": self.parent_max_tokens, "child_tokens": self.child_max_tokens,
            "overlap": self.overlap_tokens, "ocr": self.parser.ocr_enabled,
            "files": [{"path": str(path.resolve()), "checksum": file_checksum(path)} for path in files],
        }, files

    def _ensure_index(self):
        with self._lock:
            if self.store is not None:
                return
            signature, files = self._signature()
            snapshot = self.repository.load_current(signature)
            if snapshot is not None:
                self.attach_index(snapshot.store, snapshot.documents,
                                  {parent.parent_id: parent for parent in snapshot.parents})
            else:
                self._build(signature, files)

    def build_index(self):
        """Explicitly rebuild after adding/updating/removing knowledge files."""
        with self._lock:
            signature, files = self._signature()
            self._build(signature, files)

    def _build(self, signature, files):
        result = IngestionResult()
        if files:
            tokenizer = self.tokenizer
            child_budget = self.child_max_tokens
            if tokenizer is None:
                model = get_model(self.model_name)
                tokenizer = model.tokenizer
                # Include source/section prefixes in the embedding budget, not just content.
                special = tokenizer.num_special_tokens_to_add(pair=False)
                child_budget = min(child_budget, model.max_seq_length - special)
            parent_chunker = ParentChunker(tokenizer, self.parent_max_tokens)
            child_chunker = ChildChunker(tokenizer, child_budget, min(self.overlap_tokens, child_budget - 1))
            ingestion = IngestionPipeline(self.parser, parent_chunker, child_chunker)
            result = ingestion.run(self.knowledge_dir, files=files)
        indexing = IndexingPipeline(
            self.embedding_fn or partial(embed_texts, model_name=self.model_name),
            store_factory=self.store_factory,
        )
        snapshot = indexing.build(result)
        saved = self.repository.save(snapshot, signature)
        parents = {parent.parent_id: parent for parent in snapshot.parents}
        pipeline = self._prepare_pipeline(snapshot.store, parents, self.model_name)
        # All fallible construction is finished before publishing. Only references switch after it.
        self.repository.publish(saved)
        self._activate_index(snapshot.store, snapshot.documents, parents, pipeline, self.model_name)

    @property
    def pipeline(self):
        """Public composition point for standalone retrieval and evaluation routes."""
        with self._lock:
            self._ensure_index()
            return self._pipeline

    def attach_index(self, store, documents, parents, *, model_name=None):
        """Bind an in-memory/frozen index as one unit; do not write the current pointer."""
        with self._lock:
            model_name = model_name if model_name is not None else self.model_name
            pipeline = self._prepare_pipeline(store, parents, model_name)
            self._activate_index(store, documents, parents, pipeline, model_name)

    def _prepare_pipeline(self, store, parents, model_name):
        return RetrievalPipeline.from_index(
            store, parents, embed=self.embedding_fn or partial(embed_texts, model_name=model_name),
            dense_top_k=self.dense_top_k, bm25_top_k=self.bm25_top_k,
        )

    def _activate_index(self, store, documents, parents, pipeline, model_name):
        """Install prepared references under the facade lock; no construction or I/O."""
        self.store, self.documents, self.parents = store, documents, parents
        self.model_name, self._pipeline = model_name, pipeline

    def search_rankings(self, query: str, k: int = 5, strategy: str = "hybrid"):
        """Compatible Child and unique-Parent rankings from the composed pipeline."""
        if not query.strip() or k <= 0:
            return {"children": [], "parents": [], "candidate_count": 0}
        with self._lock:
            return self.pipeline.search_rankings(query, k, strategy)

    def search(self, query: str, k: int = 2):
        return self.search_rankings(query, k)["parents"]

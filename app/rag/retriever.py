"""Compatible knowledge search backed by structured, persistent hybrid retrieval."""
import json
import sqlite3
from contextlib import closing
from functools import partial
from pathlib import Path
from threading import RLock
from uuid import uuid4

import numpy as np

from app.config import (
    RAG_BM25_TOP_K, RAG_CHILD_MAX_TOKENS, RAG_CHILD_OVERLAP_TOKENS,
    RAG_DENSE_TOP_K, RAG_EMBEDDING_MODEL, RAG_KNOWLEDGE_DIR, RAG_OCR_ENABLED,
    RAG_PARENT_MAX_TOKENS, RAG_STORAGE_DIR,
)
from app.rag.chunking.child_chunker import ChildChunker
from app.rag.chunking.parent_chunker import ParentChunker
from app.rag.embedder import embed_texts, get_model
from app.rag.indexing.vector_store import FaissVectorStore, VectorStoreInterface
from app.rag.ingestion.docling_parser import DoclingParser, file_checksum
from app.rag.ingestion.pipeline import IngestionPipeline, IngestionResult
from app.rag.loader import discover_documents
from app.rag.models import DocumentRecord, ParentChunk
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

    def _embed(self, texts):
        if self.embedding_fn is not None:
            return np.asarray(self.embedding_fn(texts), dtype="float32")
        return embed_texts(texts, self.model_name)

    def _ensure_index(self):
        with self._lock:
            if self.store is not None:
                return
            signature, files = self._signature()
            if self._load(signature):
                return
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
        # Publish nothing until parsing, embedding and persistence have all succeeded.
        records = [child.model_dump(mode="json") for child in result.children]
        if records:
            vectors = self._embed([record["search_text"] for record in records])
            store = self.store_factory(vectors.shape[1])
            store.add(vectors, records)
        else:
            store = self.store_factory(1)
        self._save(signature, store, result.documents, result.parents)
        self.attach_index(store, result.documents, {parent.parent_id: parent for parent in result.parents})

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
            embed = self.embedding_fn or partial(embed_texts, model_name=model_name)
            pipeline = RetrievalPipeline.from_index(
                store, parents, embed=embed,
                dense_top_k=self.dense_top_k, bm25_top_k=self.bm25_top_k,
            )
            self.store, self.documents, self.parents = store, documents, parents
            self.model_name, self._pipeline = model_name, pipeline

    def _save(self, signature, store, documents, parents):
        root = self.storage_dir / "indexes"
        generation = uuid4().hex
        path = root / generation
        store.save(path)
        with closing(sqlite3.connect(path / "metadata.db")) as connection, connection:
            connection.executescript("""
                CREATE TABLE documents (document_id TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE parents (parent_id TEXT PRIMARY KEY, document_id TEXT, data TEXT NOT NULL);
                CREATE TABLE chunks (chunk_id TEXT PRIMARY KEY, parent_id TEXT, document_id TEXT);
            """)
            connection.executemany("INSERT INTO documents VALUES (?, ?)",
                                   [(doc.document_id, doc.model_dump_json()) for doc in documents])
            connection.executemany("INSERT INTO parents VALUES (?, ?, ?)",
                                   [(p.parent_id, p.document_id, p.model_dump_json()) for p in parents])
            connection.executemany("INSERT INTO chunks VALUES (?, ?, ?)",
                                   [(r["chunk_id"], r["parent_id"], r["document_id"]) for r in store.records])
        # Publish a complete generation in one step instead of mixing old/new index files.
        pointer = root / f".current-{generation}.tmp"
        pointer.write_text(json.dumps({"generation": generation, "signature": signature}), encoding="utf-8")
        pointer.replace(root / "current.json")

    def _load(self, signature):
        root = self.storage_dir / "indexes"
        pointer = root / "current.json"
        if not pointer.exists():
            return False
        current = json.loads(pointer.read_text(encoding="utf-8"))
        if current["signature"] != signature:
            return False
        path = root / current["generation"]
        store = self.store_factory.load(path)
        with closing(sqlite3.connect(path / "metadata.db")) as connection:
            documents = [DocumentRecord.model_validate_json(row[0]) for row in connection.execute("SELECT data FROM documents")]
            parents = [ParentChunk.model_validate_json(row[0]) for row in connection.execute("SELECT data FROM parents")]
        self.attach_index(store, documents, {parent.parent_id: parent for parent in parents})
        return True

    def search_rankings(self, query: str, k: int = 5, strategy: str = "hybrid"):
        """Compatible Child and unique-Parent rankings from the composed pipeline."""
        if not query.strip() or k <= 0:
            return {"children": [], "parents": [], "candidate_count": 0}
        with self._lock:
            return self.pipeline.search_rankings(query, k, strategy)

    def search(self, query: str, k: int = 2):
        return self.search_rankings(query, k)["parents"]

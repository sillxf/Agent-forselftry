"""Compatible knowledge search backed by structured, persistent hybrid retrieval."""
import json
import re
import sqlite3
from contextlib import closing
from pathlib import Path
from threading import RLock
from uuid import uuid4

import numpy as np
from rank_bm25 import BM25Plus

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
from app.rag.loader import discover_documents
from app.rag.models import DocumentRecord, ParentChunk
from app.rag.processing.cross_page_merger import CrossPageMerger
from app.rag.processing.structure_recovery import StructureRecovery


def tokenize(text: str) -> list[str]:
    """Keep security identifiers intact; Chinese does not depend on whitespace."""
    terms = re.findall(r"[a-z0-9]+(?:[._:/-][a-z0-9]+)*|[\u3400-\u9fff]", text.lower())
    for run in re.findall(r"[\u3400-\u9fff]{2,}", text):
        terms.extend(run[i:i + 2] for i in range(len(run) - 1))
    return terms


def reciprocal_rank_fusion(dense_results, sparse_results, rank_constant=60):
    scores, records = {}, {}
    for results in (dense_results, sparse_results):
        for rank, record in enumerate(results, 1):
            key = record["chunk_id"]
            scores[key] = scores.get(key, 0.0) + 1.0 / (rank_constant + rank)
            records[key] = {**records.get(key, {}), **record}
    keys = sorted(scores, key=lambda key: (
        -scores[key], -records[key].get("sparse_score", 0.0),
        -records[key].get("dense_score", -1.0), key,
    ))
    return [{**records[key], "score": scores[key]} for key in keys]


class KnowledgeRetriever:
    INDEX_VERSION = 3

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
        self._tokens = []
        self._bm25 = None
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
        documents, parents, children = [], [], []
        seen = set()
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
            for path in files:
                checksum = file_checksum(path)
                if checksum in seen:
                    continue
                parsed = self.parser.parse(path)
                seen.add(checksum)
                documents.append(parsed.document)
                blocks = CrossPageMerger().merge(parsed.blocks)
                blocks = StructureRecovery().recover(blocks)
                new_parents = parent_chunker.split(blocks, parsed.document)
                parents.extend(new_parents)
                for parent in new_parents:
                    children.extend(child_chunker.split(parent, parsed.document.filename, parsed.document.file_type))
        # Publish nothing until parsing, embedding and persistence have all succeeded.
        records = [child.model_dump(mode="json") for child in children]
        if records:
            vectors = self._embed([record["search_text"] for record in records])
            store = self.store_factory(vectors.shape[1])
            store.add(vectors, records)
        else:
            store = self.store_factory(1)
        self._save(signature, store, documents, parents)
        self.store, self.documents = store, documents
        self.parents = {parent.parent_id: parent for parent in parents}
        self._build_sparse()

    def _build_sparse(self):
        self._tokens = [tokenize(record["search_text"]) for record in self.store.records]
        # BM25+ avoids zero/negative IDF for identifiers in tiny knowledge bases.
        self._bm25 = BM25Plus([tokens or ["__empty__"] for tokens in self._tokens]) if self._tokens else None

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
        self.store, self.documents = store, documents
        self.parents = {parent.parent_id: parent for parent in parents}
        self._build_sparse()
        return True

    def _sparse_search(self, query, limit):
        tokens = tokenize(query)
        scores = self._bm25.get_scores(tokens)
        matches = [i for i, terms in enumerate(self._tokens) if set(tokens) & set(terms)]
        matches.sort(key=lambda i: -float(scores[i]))
        return [{**self.store.records[i], "sparse_score": float(scores[i])} for i in matches[:limit]]

    def search(self, query: str, k: int = 2):
        if not query.strip() or k <= 0:
            return []
        with self._lock:
            self._ensure_index()
            if not self.store.records:
                return []
            vector = self._embed([query])[0]
            dense = self.store.search(vector, max(self.dense_top_k, k * 4))
            sparse = self._sparse_search(query, max(self.bm25_top_k, k * 4))
            results, seen = [], set()
            for item in reciprocal_rank_fusion(dense, sparse):
                parent = self.parents[item["parent_id"]]
                if parent.parent_id in seen:
                    continue
                seen.add(parent.parent_id)
                results.append({
                    **item, "source": item["source_name"], "chunk_content": item["content"],
                    "content": parent.content, "page_start": parent.page_start, "page_end": parent.page_end,
                    "matched_page_start": item["page_start"], "matched_page_end": item["page_end"],
                    "image_paths": list(dict.fromkeys(b.image_path for b in parent.blocks if b.image_path)),
                })
                if len(results) >= k:
                    break
            return results

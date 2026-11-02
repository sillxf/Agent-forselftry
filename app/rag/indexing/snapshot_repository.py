"""Persist and publish local index generations without constructing query components."""
import json
import sqlite3
from contextlib import closing
from dataclasses import dataclass
from pathlib import Path
from uuid import uuid4

from app.rag.indexing.pipeline import IndexSnapshot
from app.rag.indexing.vector_store import FaissVectorStore
from app.rag.models import DocumentRecord, ParentChunk


@dataclass(frozen=True)
class SavedGeneration:
    generation: str
    signature: dict


class SnapshotRepository:
    def __init__(self, storage_dir, store_factory=FaissVectorStore):
        self.root = Path(storage_dir) / "indexes"
        self.store_factory = store_factory

    def save(self, snapshot: IndexSnapshot, signature: dict) -> SavedGeneration:
        """Save a fresh generation; leave the current pointer and old files untouched."""
        generation = uuid4().hex
        path = self.root / generation
        snapshot.store.save(path)
        with closing(sqlite3.connect(path / "metadata.db")) as connection, connection:
            connection.executescript("""
                CREATE TABLE documents (document_id TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE parents (parent_id TEXT PRIMARY KEY, document_id TEXT, data TEXT NOT NULL);
                CREATE TABLE chunks (chunk_id TEXT PRIMARY KEY, parent_id TEXT, document_id TEXT);
            """)
            connection.executemany("INSERT INTO documents VALUES (?, ?)",
                                   [(doc.document_id, doc.model_dump_json()) for doc in snapshot.documents])
            connection.executemany("INSERT INTO parents VALUES (?, ?, ?)",
                                   [(p.parent_id, p.document_id, p.model_dump_json()) for p in snapshot.parents])
            connection.executemany("INSERT INTO chunks VALUES (?, ?, ?)",
                                   [(r["chunk_id"], r["parent_id"], r["document_id"]) for r in snapshot.store.records])
        return SavedGeneration(generation, signature)

    def publish(self, saved: SavedGeneration) -> None:
        """Publish only after the caller has prepared a usable query pipeline."""
        pointer = self.root / f".current-{saved.generation}.tmp"
        pointer.write_text(json.dumps({"generation": saved.generation, "signature": saved.signature}), encoding="utf-8")
        pointer.replace(self.root / "current.json")

    def load_generation(self, generation: str) -> IndexSnapshot:
        path = self.root / generation
        store = self.store_factory.load(path)
        with closing(sqlite3.connect(path / "metadata.db")) as connection:
            documents = [DocumentRecord.model_validate_json(row[0]) for row in connection.execute("SELECT data FROM documents")]
            parents = [ParentChunk.model_validate_json(row[0]) for row in connection.execute("SELECT data FROM parents")]
        return IndexSnapshot(store, documents, parents)

    def load_current(self, signature: dict) -> IndexSnapshot | None:
        pointer = self.root / "current.json"
        if not pointer.exists():
            return None
        current = json.loads(pointer.read_text(encoding="utf-8"))
        if current["signature"] != signature:
            return None
        return self.load_generation(current["generation"])

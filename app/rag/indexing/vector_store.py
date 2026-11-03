"""Normalized FAISS retrieval and local persistence."""
import json
from pathlib import Path
from typing import Protocol

import faiss
import numpy as np


class VectorStoreInterface(Protocol):
    records: list[dict]

    @property
    def dimension(self) -> int: ...

    def add(self, vectors, records): ...
    def search(self, vector, k=10): ...
    def save(self, path): ...

    @classmethod
    def load(cls, path): ...


class FaissVectorStore:
    def __init__(self, dimension: int):
        self.index = faiss.IndexFlatIP(dimension)
        self.records = []

    @property
    def dimension(self):
        return self.index.d

    @property
    def documents(self):
        return self.records

    def add(self, vectors, records):
        matrix = np.array(vectors, dtype="float32", copy=True, order="C")
        if matrix.ndim != 2 or matrix.shape != (len(records), self.dimension) or not np.isfinite(matrix).all():
            raise ValueError("Invalid embedding matrix shape or nonfinite values")
        faiss.normalize_L2(matrix)
        self.index.add(matrix)
        self.records.extend(records)

    def search(self, vector, k=10):
        if k <= 0 or not self.records:
            return []
        query = np.array([vector], dtype="float32")
        faiss.normalize_L2(query)
        scores, positions = self.index.search(query, min(k, len(self.records)))
        return [{**self.records[int(pos)], "dense_score": float(score)}
                for score, pos in zip(scores[0], positions[0])]

    def updated(self, remove_ids, vectors, records):
        """Mutate a private FAISS clone, never the store serving current queries."""
        result = type(self)(self.dimension)
        result.index = faiss.clone_index(self.index)
        positions = np.asarray([i for i, r in enumerate(self.records) if r["chunk_id"] in remove_ids], dtype="int64")
        if len(positions):
            result.index.remove_ids(positions)
        result.records = [dict(r) for r in self.records if r["chunk_id"] not in remove_ids]
        if records:
            result.add(vectors, records)
        return result

    def save(self, path):
        path = Path(path)
        path.mkdir(parents=True, exist_ok=True)
        # Byte serialization also works with Windows paths containing Chinese.
        (path / "faiss.index").write_bytes(faiss.serialize_index(self.index).tobytes())
        (path / "chunks.jsonl").write_text(
            "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in self.records),
            encoding="utf-8",
        )

    @classmethod
    def load(cls, path):
        path = Path(path)
        index = faiss.deserialize_index(np.frombuffer((path / "faiss.index").read_bytes(), dtype="uint8").copy())
        store = cls(index.d)
        store.index = index
        store.records = [json.loads(line) for line in (path / "chunks.jsonl").read_text(encoding="utf-8").splitlines()]
        if store.index.ntotal != len(store.records):
            raise ValueError("Vector count differs from chunk metadata")
        return store

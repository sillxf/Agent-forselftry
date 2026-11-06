"""Query embedding and vector retrieval over an already loaded index."""

from collections import OrderedDict
from threading import Lock

import numpy as np


class DenseRetriever:
    def __init__(self, store, embed):
        self.store = store
        self.embed = embed
        self._vectors, self._lock = OrderedDict(), Lock()

    supports_filter = True

    def vector(self, query: str):
        """Query embedding, reused within a search for similarity scoring."""
        with self._lock:
            cached = self._vectors.get(query)
            if cached is not None:
                self._vectors.move_to_end(query)
                return cached
        vector = np.asarray(self.embed([query]), dtype="float32")[0]
        with self._lock:
            self._vectors[query] = vector
            while len(self._vectors) > 64:
                self._vectors.popitem(last=False)
        return vector

    def similarity(self, queries, chunk_ids):
        """Best cosine similarity over the queries for each chunk; {} if unsupported."""
        if not hasattr(self.store, "similarity") or not self.store.records:
            return {}
        best = {}
        for query in queries:
            for key, score in self.store.similarity(self.vector(query), chunk_ids).items():
                best[key] = max(score, best.get(key, -1.0))
        return best

    def retrieve(self, query: str, limit: int, *, allowed_ids=None) -> list[dict]:
        if not self.store.records:
            return []
        vector = self.vector(query)
        return (
            self.store.search_filtered(
                vector, limit, lambda r: r["document_id"] in allowed_ids
            )
            if allowed_ids is not None and hasattr(self.store, "search_filtered")
            else self.store.search(vector, limit)
        )

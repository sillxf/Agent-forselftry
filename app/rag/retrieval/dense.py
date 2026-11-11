"""Query embedding and vector retrieval over an already loaded index."""
import numpy as np


class DenseRetriever:
    def __init__(self, store, embed):
        self.store = store
        self.embed = embed

    def retrieve(self, query: str, limit: int) -> list[dict]:
        if not self.store.records:
            return []
        vector = np.asarray(self.embed([query]), dtype="float32")[0]
        return self.store.search(vector, limit)

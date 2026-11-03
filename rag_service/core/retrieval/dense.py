"""Query embedding and vector retrieval over an already loaded index."""

import numpy as np


class DenseRetriever:
    def __init__(self, store, embed):
        self.store = store
        self.embed = embed

    supports_filter = True

    def retrieve(self, query: str, limit: int, *, allowed_ids=None) -> list[dict]:
        if not self.store.records:
            return []
        vector = np.asarray(self.embed([query]), dtype="float32")[0]
        return (
            self.store.search_filtered(
                vector, limit, lambda r: r["document_id"] in allowed_ids
            )
            if allowed_ids is not None and hasattr(self.store, "search_filtered")
            else self.store.search(vector, limit)
        )

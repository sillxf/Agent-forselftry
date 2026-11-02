"""Auxiliary-view dense retrieval, mapped back to canonical source records before fusion."""
import numpy as np

from app.rag.retrieval.fusion import RRFFusion
from app.rag.views import RetrievalView, validate_views


class MultiViewUnavailable(ValueError):
    """The active generation has no auxiliary index; never silently run Hybrid instead."""


class MultiViewDenseRetriever:
    def __init__(self, original_store, view_store, embed):
        self.original_store = original_store
        self.view_store = view_store
        self.embed = embed
        self.sources = {r["chunk_id"]: r for r in original_store.records}
        views = [RetrievalView.model_validate({k: v for k, v in r.items() if k != "chunk_id"})
                 for r in view_store.records]
        validate_views(views, original_store.records)
        self.fusion = RRFFusion()

    def retrieve(self, query, limit):
        vector = np.asarray(self.embed([query]), dtype="float32")[0]
        original = self.original_store.search(vector, limit)
        # Each source has at most two question views. Overfetch before Child deduplication.
        hits = self.view_store.search(vector, limit * 2)
        candidates = {}
        for hit in hits:
            key = hit["source_child_id"]
            if key not in candidates:
                candidates[key] = {**self.sources[key], "view_score": hit["dense_score"],
                                   "matched_view_types": ["question"], "matched_view_ids": []}
            candidates[key]["matched_view_ids"].append(hit["view_id"])
        # First appearance is the best view rank; a Child receives one vote per route.
        return self.fusion.fuse([original, list(candidates.values())[:limit]])

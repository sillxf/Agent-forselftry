"""Query-time composition; components own algorithms, the pipeline owns order/limits."""

from time import perf_counter

from rag_service.core.retrieval.context import ParentContextBuilder
from rag_service.core.retrieval.dense import DenseRetriever
from rag_service.core.retrieval.fusion import RRFFusion
from rag_service.core.retrieval.sparse import SparseRetriever
from rag_service.core.retrieval.multiview import (
    MultiViewDenseRetriever,
    MultiViewUnavailable,
)


class RetrievalPipeline:
    def __init__(
        self,
        dense,
        sparse,
        fusion,
        context_builder,
        *,
        dense_top_k=20,
        bm25_top_k=20,
        multi_view_dense=None,
    ):
        self.multi_view_dense = multi_view_dense
        self.eligibility = (
            None  # Bound only for live managed runtimes, never frozen evaluation.
        )
        self.dense = dense
        self.sparse = sparse
        self.fusion = fusion
        self.context_builder = context_builder
        self.dense_top_k = dense_top_k
        self.bm25_top_k = bm25_top_k

    @classmethod
    def from_index(
        cls,
        store,
        parents,
        *,
        embed,
        dense_top_k=20,
        bm25_top_k=20,
        view_store=None,
        sparse=None,
    ):
        """Bind all query components to the same already loaded index snapshot."""
        return cls(
            DenseRetriever(store, embed),
            sparse or SparseRetriever(store.records),
            RRFFusion(),
            ParentContextBuilder(parents),
            dense_top_k=dense_top_k,
            bm25_top_k=bm25_top_k,
            multi_view_dense=MultiViewDenseRetriever(store, view_store, embed)
            if view_store is not None
            else None,
        )

    def rank_candidates(
        self, query: str, k: int, strategy: str = "hybrid", *, candidate_k=None
    ) -> list[dict]:
        if not query.strip() or k <= 0:
            return []
        if strategy not in {"dense", "bm25", "hybrid", "multi_view"}:
            raise ValueError(f"Unknown retrieval strategy: {strategy}")
        if strategy == "multi_view" and self.multi_view_dense is None:
            raise MultiViewUnavailable(
                "The active generation has no Question View index"
            )
        dense_limit = (
            candidate_k if candidate_k is not None else max(self.dense_top_k, k * 4)
        )
        sparse_limit = (
            candidate_k if candidate_k is not None else max(self.bm25_top_k, k * 4)
        )
        allowed = self.eligibility() if self.eligibility is not None else None
        if allowed == set():
            return []
        dense, sparse = [], []

        def retrieve(route, name, limit):
            started = perf_counter()
            rows = self._retrieve(route, query, limit, allowed)
            if hasattr(self, "route_trace"):
                self.route_trace.append(
                    {
                        "stage": name,
                        "elapsed_ms": (perf_counter() - started) * 1000,
                        "candidates": [
                            {
                                "chunk_id": x["chunk_id"],
                                "dense_score": x.get("dense_score"),
                                "sparse_score": x.get("sparse_score"),
                            }
                            for x in rows
                        ],
                    }
                )
            return rows

        if strategy in {"dense", "hybrid"}:
            dense = retrieve(self.dense, "dense", dense_limit)
        if strategy == "multi_view":
            dense = retrieve(self.multi_view_dense, "multi_view", dense_limit)
        if strategy in {"bm25", "hybrid", "multi_view"}:
            sparse = retrieve(self.sparse, "sparse", sparse_limit)
        if strategy in {"hybrid", "multi_view"}:
            ranked = self.fusion.fuse([dense, sparse])
            return ranked[:candidate_k] if candidate_k is not None else ranked
        return dense if strategy == "dense" else sparse

    @staticmethod
    def _retrieve(route, query, limit, allowed):
        if allowed is None:
            return route.retrieve(query, limit)
        if getattr(route, "supports_filter", False):
            return [
                r
                for r in route.retrieve(query, limit, allowed_ids=allowed)
                if r["document_id"] in allowed
            ][:limit]
        requested, maximum = limit, max(limit, min(200, limit * 4))
        while True:
            hits = route.retrieve(query, requested)
            valid = [item for item in hits if item["document_id"] in allowed]
            if len(valid) >= limit or len(hits) < requested or requested >= maximum:
                return valid[:limit]
            requested = min(maximum, requested * 2)

    def search_rankings(
        self,
        query: str,
        k: int = 5,
        strategy: str = "hybrid",
        *,
        candidate_k=None,
        reranker=None,
    ) -> dict:
        ranked = self.rank_candidates(query, k, strategy, candidate_k=candidate_k)
        if reranker is not None:
            ranked = reranker.rerank(query, ranked)
        if self.eligibility is not None:
            allowed = self.eligibility()  # Recheck after expensive embedding/reranking.
            ranked = [item for item in ranked if item["document_id"] in allowed]
        return {
            "children": [
                dict(item, source_block_ids=item["block_ids"]) for item in ranked[:k]
            ],
            "parents": self.context_builder.build(ranked, k),
            "candidate_count": len(ranked),
        }

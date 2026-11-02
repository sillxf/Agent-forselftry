"""Query-time composition; components own algorithms, the pipeline owns order/limits."""
from app.rag.retrieval.context import ParentContextBuilder
from app.rag.retrieval.dense import DenseRetriever
from app.rag.retrieval.fusion import RRFFusion
from app.rag.retrieval.sparse import SparseRetriever


class RetrievalPipeline:
    def __init__(self, dense, sparse, fusion, context_builder, *, dense_top_k=20, bm25_top_k=20):
        self.dense = dense
        self.sparse = sparse
        self.fusion = fusion
        self.context_builder = context_builder
        self.dense_top_k = dense_top_k
        self.bm25_top_k = bm25_top_k

    @classmethod
    def from_index(cls, store, parents, *, embed, dense_top_k=20, bm25_top_k=20):
        """Bind all query components to the same already loaded index snapshot."""
        return cls(DenseRetriever(store, embed), SparseRetriever(store.records), RRFFusion(),
                   ParentContextBuilder(parents), dense_top_k=dense_top_k, bm25_top_k=bm25_top_k)

    def rank_candidates(self, query: str, k: int, strategy: str = "hybrid") -> list[dict]:
        if not query.strip() or k <= 0:
            return []
        if strategy not in {"dense", "bm25", "hybrid"}:
            raise ValueError(f"Unknown retrieval strategy: {strategy}")
        dense, sparse = [], []
        if strategy in {"dense", "hybrid"}:
            dense = self.dense.retrieve(query, max(self.dense_top_k, k * 4))
        if strategy in {"bm25", "hybrid"}:
            sparse = self.sparse.retrieve(query, max(self.bm25_top_k, k * 4))
        if strategy == "hybrid":
            return self.fusion.fuse([dense, sparse])
        return dense if strategy == "dense" else sparse

    def search_rankings(self, query: str, k: int = 5, strategy: str = "hybrid") -> dict:
        ranked = self.rank_candidates(query, k, strategy)
        return {
            "children": [dict(item, source_block_ids=item["block_ids"]) for item in ranked[:k]],
            "parents": self.context_builder.build(ranked, k),
            "candidate_count": len(ranked),
        }

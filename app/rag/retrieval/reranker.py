"""Cross-encoder reranking over a bounded retrieval candidate set."""

from sentence_transformers import CrossEncoder


class BGEReranker:
    """BGE cross-encoder used after the canonical Hybrid candidate set."""

    def __init__(self, model_name="BAAI/bge-reranker-v2-m3", *, batch_size=16, max_length=512):
        self.model_name = model_name
        self.batch_size = batch_size
        self.max_length = max_length
        self.model = CrossEncoder(model_name, max_length=max_length)

    def rerank(self, query: str, candidates: list[dict]) -> list[dict]:
        if not candidates:
            return []
        pairs = [(query, candidate["content"]) for candidate in candidates]
        scores = self.model.predict(pairs, batch_size=self.batch_size, show_progress_bar=False)
        ranked = [dict(candidate, reranker_score=float(score), hybrid_rank=rank)
                  for rank, (candidate, score) in enumerate(zip(candidates, scores), 1)]
        return sorted(ranked, key=lambda item: (-item["reranker_score"], item["hybrid_rank"]))

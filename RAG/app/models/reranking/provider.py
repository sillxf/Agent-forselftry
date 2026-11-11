"""Local cross-encoder reranking adapter."""

from app.core.contracts import ModelConfig
from app.models.source import model_source


class RerankerProvider:
    def __init__(self, config, pool):
        self.config = ModelConfig.model_validate(config)
        self.pool = pool

    def rerank(self, query, candidates):
        from sentence_transformers import CrossEncoder

        c = self.config
        source, revision = model_source(c.model, c.revision)
        with self.pool.use(
            c.model_dump_json(),
            lambda: CrossEncoder(
                source,
                revision=revision,
                trust_remote_code=False,
                max_length=512,
            ),
        ) as model:
            scores = model.predict(
                [(query, x["content"]) for x in candidates],
                batch_size=c.batch_size,
                show_progress_bar=False,
            )
        return sorted(
            [
                dict(item, reranker_score=float(score))
                for item, score in zip(candidates, scores, strict=True)
            ],
            key=lambda x: -x["reranker_score"],
        )

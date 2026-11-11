"""Immutable model configuration and explicit connection probes."""

from app.models.pool import usage_context


class ModelService:
    def __init__(self, repository, providers, access, audit):
        self.repository, self.providers, self.access, self.audit = (
            repository,
            providers,
            access,
            audit,
        )

    def list(self, actor):
        self.access.authorize(actor, admin=True)
        return self.repository.models()

    def add(self, actor, configuration):
        self.access.authorize(actor, admin=True)
        identity = self.repository.add_model(configuration.model_dump())
        self.audit.audit(actor["id"], "model_added", model_id=identity)
        return self.repository.model(identity)

    def enable(self, actor, identity, enabled):
        self.access.authorize(actor, admin=True)
        self.repository.enable_model(identity, enabled)
        self.audit.audit(
            actor["id"], "model_enabled", model_id=identity, enabled=enabled
        )
        return self.repository.model(identity)

    def probe(self, actor, identity, *, confirm=False):
        self.access.authorize(actor, admin=True)
        configuration = self.repository.model(identity, require_enabled=True)["config"]
        if not confirm:
            raise ValueError(
                "Explicit confirm=true is required; probing may load a model or incur provider charges"
            )
        usage = []
        token = usage_context.set(usage)
        try:
            if configuration["kind"] == "embedding":
                vectors = self.providers.embedding("provider:" + identity).embed_query(
                    ["Connection probe"]
                )
                result = {"dimension": int(vectors.shape[1])}
            else:
                rows = self.providers.reranker("provider:" + identity).rerank(
                    "probe", [{"content": "probe"}]
                )
                result = {"score": rows[0]["reranker_score"]}
            self.audit.audit(
                actor["id"], "model_probed", model_id=identity, usage=usage
            )
            return dict(**result, model_usage=usage)
        finally:
            usage_context.reset(token)

"""Explicit composition of model providers; no dynamic plugin discovery."""

from threading import RLock
import os
from app.core.contracts import ModelConfig
from app.models.pool import ModelPool
from app.models.embedding.provider import EmbeddingProvider
from app.models.reranking.provider import RerankerProvider


class Providers:
    def __init__(
        self, repository, *, pool=None, embedding_factory=None, reranker_factory=None
    ):
        self.repository = repository
        self.pool = pool or ModelPool(int(os.getenv("RAG_MAX_LOADED_MODELS", "3")))
        self.embedding_factory = embedding_factory
        self.reranker_factory = reranker_factory
        self.embeddings = {}
        self.lock = RLock()

    def config(self, name, kind="embedding"):
        if name.startswith("provider:"):
            value = self.repository.model(name.removeprefix("provider:"))["config"]
        else:
            value = ModelConfig(
                kind=kind,
                provider="sentence_transformers"
                if kind == "embedding"
                else "cross_encoder",
                model=name,
            ).model_dump()
        if value["kind"] != kind:
            raise ValueError("Incorrect model kind")
        return value

    def embedding(self, name):
        with self.lock:
            if name not in self.embeddings:
                config = self.config(name)
                self.embeddings[name] = (
                    self.embedding_factory(config)
                    if self.embedding_factory
                    else EmbeddingProvider(config, self.pool)
                )
            return self.embeddings[name]

    def reranker(self, name):
        config = self.config(name, "reranker")
        return (
            self.reranker_factory(config)
            if self.reranker_factory
            else RerankerProvider(config, self.pool)
        )

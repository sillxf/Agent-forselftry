"""Explicit providers; immutable model configurations identify embedding spaces.
Local model memory is bounded and shared across KBs within each process.
"""

from collections import OrderedDict
from contextlib import contextmanager
from contextvars import ContextVar
from threading import RLock, BoundedSemaphore
import json, os, math
import httpx
import numpy as np
from rag_service.contracts import ModelConfig

usage_context = ContextVar("model_usage", default=None)


class ModelPool:
    def __init__(self, max_loaded=3):
        if not 1 <= max_loaded <= 16:
            raise ValueError("Model pool size must be between 1 and 16")
        self.max_loaded = max_loaded
        self.models = OrderedDict()
        self.lock = RLock()

    @contextmanager
    def use(self, key, factory):
        # Serialized local inference bounds both VRAM loading and concurrent inference.
        if not self.lock.acquire(
            timeout=float(os.getenv("RAG_MODEL_ACQUIRE_TIMEOUT_SECONDS", "5"))
        ):
            raise TimeoutError("Local model capacity is busy")
        try:
            if key not in self.models:
                while len(self.models) >= self.max_loaded:
                    self.models.popitem(last=False)
                self.models[key] = factory()
            self.models.move_to_end(key)
            yield self.models[key]
        finally:
            self.lock.release()


class EmbeddingProvider:
    def __init__(self, config, pool, *, transport=None):
        self.config = ModelConfig.model_validate(config)
        self.pool = pool
        self.transport = transport
        self.key = self.config.model_dump_json()
        self.remote_gate = BoundedSemaphore(2)

    def _local(self):
        from sentence_transformers import SentenceTransformer

        return SentenceTransformer(
            self.config.model,
            revision=None
            if self.config.revision == "default"
            else self.config.revision,
            trust_remote_code=False,
        )

    def tokenizer_and_limit(self):
        if self.config.provider == "sentence_transformers":
            with self.pool.use(self.key, self._local) as m:
                return m.tokenizer, m.max_seq_length
        from transformers import AutoTokenizer

        key = "tokenizer:" + self.config.tokenizer
        with self.pool.use(
            key,
            lambda: AutoTokenizer.from_pretrained(
                self.config.tokenizer, trust_remote_code=False
            ),
        ) as t:
            return t, min(getattr(t, "model_max_length", 8192), 8192)

    def encode(self, texts, *, query=False):
        if not texts:
            return np.empty((0, self.config.dimension or 0), dtype="float32")
        texts = [
            (self.config.query_prefix if query else self.config.document_prefix) + t
            for t in texts
        ]
        if self.config.provider == "sentence_transformers":
            with self.pool.use(self.key, self._local) as m:
                encode = (
                    (m.encode_query if query else m.encode_document)
                    if self.config.encoding == "query_document"
                    else m.encode
                )
                vectors = encode(
                    texts,
                    normalize_embeddings=True,
                    convert_to_numpy=True,
                    batch_size=self.config.batch_size,
                    show_progress_bar=False,
                )
        else:
            key = (
                os.getenv(self.config.secret_env, "") if self.config.secret_env else ""
            )
            if self.config.secret_env and not key:
                raise ValueError(
                    "Provider credential environment variable is not configured"
                )
            output = []
            usage = usage_context.get()
            prior = usage or []
            requests = math.ceil(len(texts) / self.config.batch_size)
            if requests + sum(x.get("requests", 0) for x in prior) > int(
                os.getenv("RAG_REMOTE_MAX_REQUESTS_PER_OPERATION", "128")
            ):
                raise ValueError(
                    "Remote embedding request budget exceeded before this batch"
                )
            chars = sum(map(len, texts))
            if chars + sum(x.get("input_chars", 0) for x in prior) > int(
                os.getenv("RAG_REMOTE_MAX_INPUT_CHARS_PER_OPERATION", "2000000")
            ):
                raise ValueError(
                    "Remote embedding input budget exceeded before this batch"
                )
            with (
                self.remote_gate,
                httpx.Client(
                    timeout=self.config.timeout_seconds,
                    transport=self.transport,
                    follow_redirects=False,
                ) as client,
            ):
                for start in range(0, len(texts), self.config.batch_size):
                    batch = texts[start : start + self.config.batch_size]
                    entry = {
                        "provider": "openai_compatible",
                        "model": self.config.model,
                        "reported_usage": None,
                        "requests": 1,
                        "input_chars": sum(map(len, batch)),
                    }
                    if usage is not None:
                        usage.append(entry)
                    r = client.post(
                        self.config.base_url.rstrip("/") + "/embeddings",
                        headers={"Authorization": "Bearer " + key} if key else {},
                        json={
                            "model": self.config.model,
                            "input": batch,
                            "encoding_format": "float",
                        },
                    )
                    r.raise_for_status()
                    data = r.json()
                    items = sorted(data["data"], key=lambda x: x["index"])
                    if [x["index"] for x in items] != list(range(len(batch))):
                        raise ValueError("Embedding provider returned invalid indices")
                    output.extend(x["embedding"] for x in items)
                    entry["reported_usage"] = data.get("usage")
            vectors = np.asarray(output, dtype="float32")
        vectors = np.asarray(vectors, dtype="float32")
        if (
            vectors.ndim != 2
            or len(vectors) != len(texts)
            or not np.isfinite(vectors).all()
        ):
            raise ValueError("Invalid embedding matrix")
        if self.config.dimension and vectors.shape[1] != self.config.dimension:
            raise ValueError(
                "Embedding dimension differs from configured model version"
            )
        if (np.linalg.norm(vectors, axis=1) == 0).any():
            raise ValueError("Zero embedding vector")
        return vectors

    def embed_documents(self, texts):
        return self.encode(texts)

    def embed_query(self, texts):
        return self.encode(texts, query=True)


class RerankerProvider:
    def __init__(self, config, pool):
        self.config = ModelConfig.model_validate(config)
        self.pool = pool

    def rerank(self, query, candidates):
        from sentence_transformers import CrossEncoder

        c = self.config
        with self.pool.use(
            c.model_dump_json(),
            lambda: CrossEncoder(
                c.model,
                revision=None if c.revision == "default" else c.revision,
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


class Providers:
    def __init__(
        self, catalog, *, pool=None, embedding_factory=None, reranker_factory=None
    ):
        self.catalog = catalog
        self.pool = pool or ModelPool(int(os.getenv("RAG_MAX_LOADED_MODELS", "3")))
        self.embedding_factory = embedding_factory
        self.reranker_factory = reranker_factory
        self.embeddings = {}
        self.lock = RLock()

    def config(self, name, kind="embedding"):
        if name.startswith("provider:"):
            value = self.catalog.model(name.removeprefix("provider:"))["config"]
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

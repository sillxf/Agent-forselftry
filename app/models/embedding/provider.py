"""Local and compatible-HTTP embedding adapters."""

from threading import BoundedSemaphore
from pathlib import Path
from app.models.source import model_source
import os, math
import httpx
import numpy as np
from app.core.contracts import ModelConfig
from app.models.pool import usage_context


class EmbeddingProvider:
    def __init__(self, config, pool, *, transport=None):
        self.config = ModelConfig.model_validate(config)
        self.pool = pool
        self.transport = transport
        self.key = self.config.model_dump_json()
        self.remote_gate = BoundedSemaphore(2)

    def _local(self):
        from sentence_transformers import SentenceTransformer

        source, revision = model_source(self.config.model, self.config.revision)
        return SentenceTransformer(
            source,
            revision=revision,
            local_files_only=Path(source).is_dir(),
            trust_remote_code=False,
        )

    def tokenizer_and_limit(self):
        if self.config.provider == "sentence_transformers":
            with self.pool.use(self.key, self._local) as m:
                return m.tokenizer, m.max_seq_length
        from transformers import AutoTokenizer

        key = "tokenizer:" + self.config.tokenizer
        source, _ = model_source(self.config.tokenizer, require_weights=False)
        with self.pool.use(
            key,
            lambda: AutoTokenizer.from_pretrained(
                source, trust_remote_code=False, local_files_only=Path(source).is_dir()
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

"""Remote reranking over a Cohere-compatible POST {base_url}/rerank endpoint.

Cohere, Jina, vLLM and Infinity accept this request shape. Unlike the local
cross-encoder it does not hold the process model lock, so a slow rerank no
longer blocks query embedding, and several reranks may run at once.
"""

import math
import os
from threading import Lock

import httpx

from app.core.contracts import ModelConfig
from app.models.pool import usage_context


class RemoteRerankerProvider:
    def __init__(self, config, *, transport=None):
        self.config = ModelConfig.model_validate(config)
        self.transport = transport
        # Read by the orchestrator: how many reranks may be in flight per base.
        self.concurrency = int(os.getenv("RAG_REMOTE_RERANK_CONCURRENCY", "4"))
        self._client, self._lock = None, Lock()

    def _http(self):
        with self._lock:
            if self._client is None:
                self._client = httpx.Client(
                    timeout=self.config.timeout_seconds,
                    transport=self.transport,
                    follow_redirects=False,
                )
            return self._client

    def rerank(self, query, candidates):
        if not candidates:
            return []
        c = self.config
        key = os.getenv(c.secret_env, "") if c.secret_env else ""
        if c.secret_env and not key:
            raise ValueError("Provider credential environment variable is not configured")
        documents = [x["content"] for x in candidates]
        usage = usage_context.get()
        prior = usage or []
        chars = len(query) * len(documents) + sum(map(len, documents))
        if chars + sum(x.get("input_chars", 0) for x in prior) > int(
            os.getenv("RAG_REMOTE_MAX_INPUT_CHARS_PER_OPERATION", "2000000")
        ) or 1 + sum(x.get("requests", 0) for x in prior) > int(
            os.getenv("RAG_REMOTE_MAX_REQUESTS_PER_OPERATION", "128")
        ):
            raise ValueError("Remote rerank budget exceeded before this request")
        entry = {
            "provider": "cohere_compatible",
            "model": c.model,
            "reported_usage": None,
            "requests": 1,
            "input_chars": chars,
        }
        if usage is not None:
            usage.append(entry)
        response = self._http().post(
            c.base_url.rstrip("/") + "/rerank",
            headers={"Authorization": "Bearer " + key} if key else {},
            json={
                "model": c.model,
                "query": query,
                "documents": documents,
                "top_n": len(documents),
                "return_documents": False,
            },
        )
        response.raise_for_status()
        data = response.json()
        entry["reported_usage"] = data.get("usage") or data.get("meta")
        scores = {}
        for item in data["results"]:
            index, score = item["index"], float(item["relevance_score"])
            if not isinstance(index, int) or not 0 <= index < len(documents):
                raise ValueError("Reranker returned an unknown index")
            if index in scores or not math.isfinite(score):
                raise ValueError("Reranker returned a duplicate or nonfinite score")
            scores[index] = score
        if len(scores) != len(documents):
            raise ValueError("Reranker did not score every candidate")
        return sorted(
            [dict(item, reranker_score=scores[i]) for i, item in enumerate(candidates)],
            key=lambda x: -x["reranker_score"],
        )

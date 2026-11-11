"""Knowledge access through the RAG service REST API (scoped read-only key).

The agent never imports the retrieval engine; it is a normal API client, so the
service's permissions, quotas and audit apply.
"""

import os

import httpx


class KnowledgeUnavailable(RuntimeError):
    """The RAG service could not answer; carries a model-safe category."""

    def __init__(self, category, retryable):
        super().__init__(category)
        self.category, self.retryable = category, retryable


class RAGKnowledge:
    def __init__(self, url=None, token=None, knowledge_base_ids=None, *, transport=None,
                 timeout=None):
        self.knowledge_base_ids = knowledge_base_ids or [
            x for x in os.getenv("RAG_SERVICE_KNOWLEDGE_BASES", "").split(",") if x
        ]
        if not self.knowledge_base_ids:
            raise ValueError("Set RAG_SERVICE_KNOWLEDGE_BASES to the knowledge base ids")
        self.client = httpx.Client(
            base_url=(url or os.getenv("RAG_SERVICE_URL", "http://127.0.0.1:8090")).rstrip("/"),
            headers={"Authorization": "Bearer " + (token or os.environ["RAG_SERVICE_TOKEN"])},
            timeout=timeout or float(os.getenv("RAG_CLIENT_TIMEOUT", "60")),
            transport=transport,
            follow_redirects=False,
        )

    def search(self, query, *, queries=(), top_k=5, min_score=None, include_trace=False):
        payload = {
            "query": query,
            "queries": list(queries),
            "knowledge_base_ids": self.knowledge_base_ids,
            "top_k": top_k,
            "include_trace": include_trace,
        }
        if min_score is not None:
            payload["min_score"] = min_score
        try:
            response = self.client.post(
                "/api/v1/search",
                json=payload,
            )
        except httpx.TimeoutException as exc:
            raise KnowledgeUnavailable("timeout", True) from exc
        except httpx.HTTPError as exc:
            raise KnowledgeUnavailable("unreachable", True) from exc
        code = None
        if not response.is_success:
            try:
                code = response.json().get("code")
            except ValueError:
                pass
        # The service names the cause (1.3+): an unbuilt or damaged knowledge base
        # is not a transient overload, so the model is told not to retry it.
        if code == "not_published":
            raise KnowledgeUnavailable("not_published", False)
        if code == "index_integrity":
            raise KnowledgeUnavailable("index_damaged", False)
        if response.status_code in {429, 503}:
            raise KnowledgeUnavailable("busy", True)
        if response.status_code in {401, 403}:
            raise KnowledgeUnavailable("not_authorized", False)
        if response.status_code == 422:
            raise KnowledgeUnavailable("invalid_query", False)
        if not response.is_success:
            raise KnowledgeUnavailable(f"http_{response.status_code}", False)
        return response.json()

    def close(self):
        self.client.close()

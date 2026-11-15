"""Knowledge access through the RAG service REST API (scoped read-only key).

The agent never imports the retrieval engine; it is a normal API client, so the
service's permissions, quotas and audit apply.
"""

import os
import re

import httpx


class KnowledgeUnavailable(RuntimeError):
    """The RAG service could not answer; carries a model-safe category."""

    def __init__(self, category, retryable, diagnostics=None):
        super().__init__(category)
        self.category, self.retryable = category, retryable
        self.diagnostics = diagnostics or {}


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
        body = None
        if not response.is_success:
            try:
                body = response.json()
                code = body.get("code") if isinstance(body, dict) else None
            except (ValueError, TypeError):
                pass
        diagnostics = _response_diagnostics(body)
        # The service names the cause (1.3+): an unbuilt or damaged knowledge base
        # is not a transient overload, so the model is told not to retry it.
        if code == "not_published":
            raise KnowledgeUnavailable("not_published", False, diagnostics)
        if code == "index_integrity":
            raise KnowledgeUnavailable("index_damaged", False, diagnostics)
        if response.status_code in {429, 503}:
            raise KnowledgeUnavailable("busy", True, diagnostics)
        if response.status_code in {401, 403}:
            raise KnowledgeUnavailable("not_authorized", False, diagnostics)
        if response.status_code == 422:
            raise KnowledgeUnavailable("invalid_query", False, diagnostics)
        if not response.is_success:
            raise KnowledgeUnavailable(f"http_{response.status_code}", False, diagnostics)
        return response.json()

    def close(self):
        self.client.close()


def _response_diagnostics(body):
    """Keep trace identifiers and data, never error details or headers."""
    if not isinstance(body, dict):
        return {}
    diagnostics = {key: body[key] for key in ("request_id", "generation_id") if key in body}
    if "trace" in body:
        diagnostics["trace"] = safe_trace(body["trace"])
    return diagnostics


_PRIVATE_TRACE_KEYS = {
    "authorization", "headers", "api_key", "apikey", "token", "secret",
    "client_secret", "access_token", "refresh_token", "password", "credential",
    "credentials", "cookie", "set_cookie",
}
_BEARER_VALUE = re.compile(r"(?i)(\bbearer\s+)[A-Za-z0-9._~+/=-]+")


def safe_trace(value):
    """Remove credential/header fields from service diagnostics before persistence."""
    if isinstance(value, dict):
        return {
            key: safe_trace(item)
            for key, item in value.items()
            if (
                str(key).casefold().replace("-", "_") not in _PRIVATE_TRACE_KEYS
                and not str(key).casefold().endswith(("_header", "_headers", "_token", "_secret"))
                and "authorization" not in str(key).casefold()
            )
        }
    if isinstance(value, list):
        return [safe_trace(item) for item in value]
    if isinstance(value, str):
        return _BEARER_VALUE.sub(r"\1[REDACTED]", value)
    return value

"""Lightweight HTTP client: no parser, FAISS, model or server imports."""

import os
from types import SimpleNamespace
import httpx


class RAGClient:
    def __init__(
        self, url=None, token=None, knowledge_base_ids=None, *, transport=None
    ):
        self.url = (url or os.environ["RAG_SERVICE_URL"]).rstrip("/")
        self.token = token or os.environ["RAG_SERVICE_TOKEN"]
        self.knowledge_base_ids = knowledge_base_ids or [
            x for x in os.getenv("RAG_SERVICE_KNOWLEDGE_BASES", "").split(",") if x
        ]
        self.client = httpx.Client(
            base_url=self.url,
            headers={"Authorization": "Bearer " + self.token},
            timeout=float(os.getenv("RAG_CLIENT_TIMEOUT", "60")),
            transport=transport,
            follow_redirects=False,
        )

    def request(self, method, path, **kwargs):
        response = self.client.request(method, "/api/v1" + path, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            raise RuntimeError(
                "RAG service returned HTTP " + str(response.status_code)
            ) from exc
        return response.json()

    def list_knowledge_bases(self):
        return self.request("GET", "/knowledge-bases")

    def list_documents(self, kb_id):
        return self.request("GET", f"/knowledge-bases/{kb_id}/documents")

    def get_document(self, kb_id, document_id, **params):
        return self.request(
            "GET",
            f"/knowledge-bases/{kb_id}/documents/{document_id}",
            params={k: v for k, v in params.items() if v is not None},
        )

    def get_chunk(self, kb_id, chunk_id, **params):
        return self.request(
            "GET",
            f"/knowledge-bases/{kb_id}/chunks/{chunk_id}",
            params={k: v for k, v in params.items() if v is not None},
        )

    def get_context(self, kb_id, chunk_id, **params):
        return self.request(
            "GET",
            f"/knowledge-bases/{kb_id}/chunks/{chunk_id}/context",
            params={k: v for k, v in params.items() if v is not None},
        )

    def search_request(self, **kwargs):
        return self.request("POST", "/search", json=kwargs)

    def search_with_trace(self, query, k=5, *, supplement=False, as_of=None):
        if not self.knowledge_base_ids:
            raise RuntimeError("RAG_SERVICE_KNOWLEDGE_BASES is required")
        return self.search_request(
            query=query,
            knowledge_base_ids=self.knowledge_base_ids,
            top_k=k,
            supplement=supplement,
            as_of=as_of,
            include_trace=True,
        )

    def search(self, query, k=5, **kwargs):
        return self.search_with_trace(query, k)["results"]

    @property
    def orchestrator(self):
        # Read the authorized server policy; do not enable the supplementary tool by guesswork.
        bases = self.list_knowledge_bases()
        enabled = any(
            k["id"] in self.knowledge_base_ids and k["profile"]["multi_view_enabled"]
            for k in bases
        )
        return SimpleNamespace(policy=SimpleNamespace(multi_view_enabled=enabled))

    def close(self):
        self.client.close()

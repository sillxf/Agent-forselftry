"""Read-only retrieval tools; all access is delegated to the authorized target."""

from typing import Any
from mcp.server.fastmcp import Context


def register(mcp, target):
    @mcp.tool(
        structured_output=True,
        description=(
            "Search original source evidence. Models/policy are server-controlled; "
            "supplement is an explicit request, not an evidence-sufficiency assessment. "
            "queries: up to 4 optional rewrites of the same question, retrieved and "
            "fused with the original. Most useful: a translation into the documents' "
            "language (e.g. English for English sources), or a version using the "
            "documents' own terminology. Do not add facts the user did not ask about."
        ),
    )
    def rag_search(
        query: str,
        knowledge_base_ids: list[str],
        ctx: Context,
        top_k: int = 5,
        queries: list[str] | None = None,
        supplement: bool = False,
        mode: str = "default",
        filters: dict | None = None,
        as_of: str | None = None,
    ) -> dict[str, Any]:
        return target(ctx).search_request(
            query=query,
            queries=queries or [],
            knowledge_base_ids=knowledge_base_ids,
            top_k=top_k,
            supplement=supplement,
            mode=mode,
            filters=filters or {},
            as_of=as_of,
        )

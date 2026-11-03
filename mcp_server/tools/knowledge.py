"""Read-only knowledge tools; all access is delegated to the authorized target."""

from typing import Any
from mcp.server.fastmcp import Context


def register(mcp, target):
    @mcp.tool(
        structured_output=True,
        description="List only knowledge bases authorized for this caller.",
    )
    def rag_list_knowledge_bases(ctx: Context) -> dict[str, Any]:
        return {"knowledge_bases": target(ctx).list_knowledge_bases()}

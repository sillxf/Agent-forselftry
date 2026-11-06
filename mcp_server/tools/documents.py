"""Read-only documents tools; all access is delegated to the authorized target."""

from typing import Any
from mcp.server.fastmcp import Context


def register(mcp, target):
    @mcp.tool(
        structured_output=True,
        description="List authorized document identities, versions and publication states. Paginated to avoid unbounded tool output.",
    )
    def rag_list_documents(
        knowledge_base_id: str, ctx: Context, offset: int = 0, limit: int = 30
    ) -> dict[str, Any]:
        if offset < 0 or not 1 <= limit <= 100:
            raise ValueError("Invalid pagination")
        rows = target(ctx).list_documents(knowledge_base_id)
        # No local paths or internal task details are needed by an Agent.
        return {
            "documents": [
                {
                    k: v
                    for k, v in d.items()
                    if k
                    in {
                        "document_id",
                        "name",
                        "status",
                        "latest_version_id",
                        "published",
                        "metadata",
                        "file_type",
                    }
                }
                for d in rows[offset : offset + limit]
            ],
            "total": len(rows),
            "offset": offset,
        }

    @mcp.tool(
        structured_output=True,
        description="Read a bounded page of a document's published canonical content. Use generation_id from search to pin the evidence version.",
    )
    def rag_get_document(
        knowledge_base_id: str,
        document_id: str,
        ctx: Context,
        generation_id: str | None = None,
        offset: int = 0,
        limit: int = 10,
    ) -> dict[str, Any]:
        if offset < 0 or not 1 <= limit <= 30:
            raise ValueError("Invalid pagination")
        data = target(ctx).get_document(
            knowledge_base_id,
            document_id,
            generation_id=generation_id,
            offset=offset,
            limit=limit,
        )
        return {
            "document_id": document_id,
            "generation_id": data["generation_id"],
            "pagination": data["pagination"],
            "children": data["children"],
        }

    @mcp.tool(
        structured_output=True,
        description="Read one canonical evidence chunk from an authorized knowledge base and optional retained generation.",
    )
    def rag_get_chunk(
        knowledge_base_id: str,
        chunk_id: str,
        ctx: Context,
        generation_id: str | None = None,
    ) -> dict[str, Any]:
        return target(ctx).get_chunk(
            knowledge_base_id, chunk_id, generation_id=generation_id
        )

    @mcp.tool(
        structured_output=True,
        description=(
            "Read what surrounds a search hit, in reading order within the same "
            "document: unit='child' returns neighbouring chunks, unit='parent' "
            "neighbouring sections. Use it when a hit is cut off or refers to text "
            "just before or after it. before/after: 0-5."
        ),
    )
    def rag_get_context(
        knowledge_base_id: str,
        chunk_id: str,
        ctx: Context,
        before: int = 1,
        after: int = 1,
        unit: str = "child",
        generation_id: str | None = None,
    ) -> dict[str, Any]:
        return target(ctx).get_context(
            knowledge_base_id,
            chunk_id,
            before=before,
            after=after,
            unit=unit,
            generation_id=generation_id,
        )

    @mcp.tool(
        structured_output=True,
        description="Read the published document outline for long-document navigation.",
    )
    def rag_get_document_outline(
        knowledge_base_id: str,
        document_id: str,
        ctx: Context,
        generation_id: str | None = None,
    ) -> dict[str, Any]:
        data = target(ctx).get_document(
            knowledge_base_id, document_id, generation_id=generation_id, limit=1
        )
        return {
            "document_id": document_id,
            "generation_id": data["generation_id"],
            "outline": data["outline"],
        }

"""Dify External Knowledge API adapter (POST {endpoint}/retrieval).

Register http://<host>:8090/api/v1/dify as the endpoint in Dify and a read-only key
of this service as its API key; the External Knowledge ID is the knowledge base id.
Contract: https://docs.dify.ai/en/cloud/use-dify/knowledge/external-knowledge-api
Errors use Dify's suggested codes: 1001/1002 authorization, 2001 unknown base.
"""

from typing import Any

from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field

from app.core.exceptions import AccessDenied

# Dify operator -> this service's filter operator. Unknown operators are rejected.
OPERATORS = {
    "is": "$eq", "=": "$eq", "is not": "$ne", "≠": "$ne", "in": "$in", "not in": "$nin",
    "contains": "$contains", ">": "$gt", "≥": "$gte", "<": "$lt", "≤": "$lte",
    "after": "$gt", "before": "$lt",
}


class RetrievalSetting(BaseModel):
    model_config = ConfigDict(extra="ignore")
    top_k: int = Field(5, ge=1, le=20)
    score_threshold: float = Field(0.0, ge=0, le=1)


class DifyRequest(BaseModel):
    model_config = ConfigDict(extra="ignore")
    knowledge_id: str = Field(min_length=1, max_length=100)
    query: str = Field(min_length=1, max_length=4000)
    retrieval_setting: RetrievalSetting = Field(default_factory=RetrievalSetting)
    metadata_condition: dict[str, Any] | None = None


def _filters(condition):
    if not condition or not condition.get("conditions"):
        return {}
    parts = []
    for item in condition["conditions"]:
        name, operator = item.get("name"), item.get("comparison_operator")
        field = name if name in {"document_id", "file_type", "source"} else f"metadata.{name}"
        if operator == "empty":
            parts.append({field: {"$exists": False}})
        elif operator == "not empty":
            parts.append({field: {"$exists": True}})
        elif operator in OPERATORS:
            parts.append({field: {OPERATORS[operator]: item.get("value")}})
        else:
            raise ValueError(f"Unsupported comparison operator: {operator}")
    key = "$or" if condition.get("logical_operator") == "or" else "$and"
    return {key: parts}


def _error(status, code, message):
    return JSONResponse({"error_code": code, "error_msg": message}, status)


def create_router(service, actor, admin, application):
    app = APIRouter()

    @app.post("/api/v1/dify/retrieval")
    def retrieval(body: DifyRequest, who=Depends(actor)):
        try:
            service.access.authorize(who, body.knowledge_id)
        except AccessDenied:
            return _error(403, 1002, "Authorization failed for this knowledge base")
        except KeyError:
            return _error(404, 2001, "The knowledge does not exist")
        setting = body.retrieval_setting
        output = service.retrieval.search(
            who,
            dict(
                query=body.query,
                knowledge_base_ids=[body.knowledge_id],
                top_k=setting.top_k,
                filters=_filters(body.metadata_condition),
                min_score=setting.score_threshold or None,
            ),
        )
        return {
            "records": [
                {
                    "content": r["content"],
                    "score": r["relevance"] if r.get("relevance") is not None else 0.0,
                    "title": r.get("source") or r.get("source_name") or "",
                    "metadata": {
                        "document_id": r["document_id"],
                        "chunk_id": r["chunk_id"],
                        "section": " > ".join(r.get("section_path") or []),
                        "page_start": r.get("page_start"),
                        "page_end": r.get("page_end"),
                        "relevance_source": r.get("relevance_source"),
                    },
                }
                for r in output["results"]
            ]
        }

    return app

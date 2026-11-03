"""Validated administrator policy; no per-query model-selected retrieval strategy."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class RetrievalPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    default_strategy: Literal["hybrid", "hybrid_rerank"] = "hybrid"
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    candidate_k: int = Field(default=20, ge=20, le=100)
    max_top_k: int = Field(default=20, ge=1, le=20)
    max_query_chars: int = Field(default=4000, ge=1, le=4000)
    max_context_chars: int = Field(default=24000, ge=1)
    reranker_timeout_seconds: float = Field(default=2.0, gt=0, le=120)

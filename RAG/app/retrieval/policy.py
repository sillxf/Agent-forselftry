"""Validated administrator policy; no per-query model-selected retrieval strategy."""

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


class RetrievalPolicy(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    default_strategy: Literal["dense", "bm25", "hybrid", "hybrid_rerank"] = "hybrid"
    multi_view_enabled: bool = False
    supplement_candidate_k: int = Field(default=20, ge=1, le=100)
    reranker_model: str = "BAAI/bge-reranker-v2-m3"
    candidate_k: int = Field(default=20, ge=20, le=100)
    max_top_k: int = Field(default=20, ge=1, le=20)
    max_query_chars: int = Field(default=4000, ge=1, le=4000)
    # Counted with the snapshot's embedding tokenizer, the same unit as chunk budgets.
    # 8000 = five default 1600-token parents.
    max_context_tokens: int = Field(default=8000, ge=64, le=200000)
    reranker_timeout_seconds: float = Field(default=2.0, gt=0, le=120)
    parent_context: bool = True

    @model_validator(mode="before")
    @classmethod
    def _drop_character_budget(cls, value):
        # Profiles saved before 1.2 stored a character budget. Characters per token
        # differ by language, so the old number is not converted; the default applies.
        if isinstance(value, dict) and "max_context_chars" in value:
            value = {k: v for k, v in value.items() if k != "max_context_chars"}
        return value

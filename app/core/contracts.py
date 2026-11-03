"""Versioned public contracts. Build settings and live query policy are deliberately separate."""

from typing import Any, Literal
from pydantic import BaseModel, ConfigDict, Field, model_validator
from app.retrieval.policy import RetrievalPolicy


class Contract(BaseModel):
    model_config = ConfigDict(extra="forbid")


class IndexBuildConfig(Contract):
    schema_version: Literal[1] = 1
    embedding_id: str = "default-embedding"
    parent_tokens: int = Field(1600, ge=64, le=16000)
    child_tokens: int = Field(400, ge=32, le=4000)
    overlap_tokens: int = Field(60, ge=0, le=1000)
    ocr_enabled: bool = True

    @model_validator(mode="after")
    def budgets(self):
        if (
            self.overlap_tokens >= self.child_tokens
            or self.child_tokens > self.parent_tokens
        ):
            raise ValueError("Require overlap < child <= parent token budgets")
        return self


class RetrievalProfile(RetrievalPolicy):
    # Inherits strict/frozen policy. No evidence-sufficiency detection.
    default_strategy: Literal["dense", "bm25", "hybrid", "hybrid_rerank"] = "hybrid"
    reranker_id: str = "default-reranker"
    candidate_k: int = Field(20, ge=1, le=100)
    parent_context: bool = True


class KnowledgeBaseCreate(Contract):
    name: str = Field(min_length=1, max_length=120)
    description: str = Field("", max_length=2000)
    build: IndexBuildConfig = Field(default_factory=IndexBuildConfig)
    profile: RetrievalProfile = Field(default_factory=RetrievalProfile)


class SearchRequest(Contract):
    query: str = Field(min_length=1, max_length=4000)
    knowledge_base_ids: list[str] = Field(min_length=1, max_length=5)
    top_k: int = Field(5, ge=1, le=20)
    mode: Literal["default", "high_recall"] = "default"
    supplement: bool = False
    filters: dict[str, str | list[str]] = Field(default_factory=dict)
    as_of: str | None = None
    include_trace: bool = False

    @model_validator(mode="after")
    def valid(self):
        if not self.query.strip():
            raise ValueError("Query must not be blank")
        if len(set(self.knowledge_base_ids)) != len(self.knowledge_base_ids):
            raise ValueError("Duplicate knowledge base")
        if len(self.filters) > 10:
            raise ValueError("At most ten metadata filters")
        return self


class ModelConfig(Contract):
    kind: Literal["embedding", "reranker"]
    provider: Literal["sentence_transformers", "openai_compatible", "cross_encoder"]
    model: str = Field(min_length=1, max_length=300)
    revision: str = Field("default", min_length=1, max_length=200)
    dimension: int | None = Field(None, ge=1, le=65536)
    normalize: Literal[True] = True
    metric: Literal["cosine"] = "cosine"
    query_prefix: str = Field("", max_length=1000)
    document_prefix: str = Field("", max_length=1000)
    encoding: Literal["encode", "query_document"] = "encode"
    tokenizer: str | None = Field(None, max_length=300)
    base_url: str | None = Field(None, max_length=1000)
    secret_env: str | None = Field(None, pattern=r"^[A-Z][A-Z0-9_]{0,100}$")
    timeout_seconds: float = Field(30, gt=0, le=180)
    batch_size: int = Field(16, ge=1, le=128)

    @model_validator(mode="after")
    def compatible(self):
        if self.kind == "reranker" and self.provider != "cross_encoder":
            raise ValueError("Reranker requires cross_encoder")
        if self.kind == "embedding" and self.provider == "cross_encoder":
            raise ValueError("Embedding provider required")
        if self.provider == "openai_compatible" and not (
            self.base_url and self.dimension and self.tokenizer
        ):
            raise ValueError(
                "Remote embedding requires base_url, dimension and an explicit tokenizer"
            )
        if self.provider == "openai_compatible":
            from urllib.parse import urlsplit

            u = urlsplit(self.base_url)
            if (
                u.scheme not in {"http", "https"}
                or not u.hostname
                or u.username
                or u.password
                or u.query
                or u.fragment
            ):
                raise ValueError(
                    "Invalid provider URL; credentials belong in secret_env"
                )
        return self


class KeyCreate(Contract):
    name: str = Field(min_length=1, max_length=120)
    knowledge_base_ids: list[str] = Field(min_length=1, max_length=100)
    requests_per_minute: int = Field(60, ge=1, le=10000)


class JobRequest(Contract):
    operation: Literal["build", "rollback", "purge", "gc"] = "build"
    full: bool = False
    generation_id: str | None = None
    document_id: str | None = None
    confirm: bool = False

    @model_validator(mode="after")
    def arguments(self):
        if self.operation == "rollback" and not self.generation_id:
            raise ValueError("generation_id required")
        if self.operation == "purge" and not (self.document_id and self.confirm):
            raise ValueError("Explicit purge confirmation required")
        return self


class EvidenceCitation(Contract):
    knowledge_base_id: str
    document_id: str
    version_id: str | None = None
    chunk_id: str
    page_start: int | None = None
    page_end: int | None = None


class SearchEvidence(BaseModel):
    # Route scores and source-specific metadata are extensible; source identity is stable.
    model_config = ConfigDict(extra="allow")
    knowledge_base_id: str
    document_id: str
    version_id: str | None = None
    parent_id: str
    chunk_id: str
    generation_id: str
    content: str
    citation: EvidenceCitation


class SearchMetadata(Contract):
    snapshots: list[dict[str, Any]]
    elapsed_ms: float
    model_usage: list[dict[str, Any]]
    warnings: list[str]


class SearchResponse(Contract):
    schema_version: Literal[1] = 1
    request_id: str
    query: str
    results: list[SearchEvidence]
    metadata: SearchMetadata
    trace: list[dict[str, Any]] | None = None

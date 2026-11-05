"""Source-preserving records shared by ingestion, chunking and retrieval."""

from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

BlockType = Literal[
    "heading",
    "paragraph",
    "table",
    "image",
    "list",
    "code",
    "page_header",
    "page_footer",
]
StructureSource = Literal["original", "inferred", "unknown"]


class DocumentRecord(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    file_type: str
    source_path: str
    checksum: str
    title: str | None = None
    version: str = ""
    version_id: str | None = None
    artifact_id: str | None = None
    source_blob_path: str | None = None
    processing_signature: dict[str, Any] | None = None
    lifecycle_state: dict[str, Any] | None = None


class KnowledgeDocument(BaseModel):
    """Mutable source identity; the published generation owns the served version."""

    document_id: str
    source_key: str
    source_path: str
    latest_version_id: str | None = None
    created_at: str
    updated_at: str
    deleted_at: str | None = None
    effective_at: str | None = None
    expires_at: str | None = None
    selected_version_id: str | None = None
    purged_at: str | None = None
    # Informational: listed as due for human review; never changes visibility.
    review_after: str | None = None
    # Hidden from live retrieval while this replacement exists and is not deleted.
    superseded_by: str | None = None
    metadata: dict[str, str] = Field(default_factory=dict)
    view_config: dict[str, Any] = Field(default_factory=dict)


class DocumentVersion(BaseModel):
    """Immutable source bytes, independent of parsing and indexing configuration."""

    version_id: str
    document_id: str
    version_number: int
    content_hash: str
    source_blob_path: str
    file_type: str
    created_at: str


class BlockLayout(BaseModel):
    source_label: str | None = None
    container_type: Literal["picture", "table"] | None = None
    font_size: float | None = None
    line_height: float | None = None
    bold: bool = False
    indent: float | None = None
    top: float | None = None
    bottom: float | None = None
    page_height: float | None = None


class ContentBlock(BaseModel):
    block_id: str = Field(default_factory=lambda: str(uuid4()))
    document_id: str
    block_type: BlockType
    text: str = ""
    page_number: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    section_path: list[str] = Field(default_factory=list)
    table_data: list[dict[str, Any]] | None = None
    table_columns: list[str] = Field(default_factory=list)
    image_path: str | None = None
    caption: str | None = None
    related_block_ids: list[str] = Field(default_factory=list)
    structure_source: StructureSource = "original"
    heading_level: int | None = None
    list_marker: str | None = None
    layout: BlockLayout = Field(default_factory=BlockLayout)
    source_block_ids: list[str] = Field(default_factory=list)
    merge_reason: str | None = None
    structure_reason: str | None = None
    structure_confidence: float | None = None


class ParsedDocument(BaseModel):
    document: DocumentRecord
    blocks: list[ContentBlock] = Field(default_factory=list)
    markdown: str = ""
    structured_data: dict[str, Any] = Field(default_factory=dict)


class ParentChunk(BaseModel):
    parent_id: str = Field(default_factory=lambda: str(uuid4()))
    retrieval_key: str | None = None
    document_id: str
    version_id: str | None = None
    artifact_id: str | None = None
    source_checksum: str | None = None
    section_path: list[str] = Field(default_factory=list)
    content: str
    page_start: int | None = None
    page_end: int | None = None
    blocks: list[ContentBlock] = Field(default_factory=list)


class ChildChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    retrieval_key: str | None = None
    parent_id: str
    document_id: str
    version_id: str | None = None
    artifact_id: str | None = None
    source_checksum: str | None = None
    source_name: str
    file_type: str = ""
    content: str
    search_text: str
    page_start: int | None = None
    page_end: int | None = None
    section_path: list[str] = Field(default_factory=list)
    chunk_type: str = "text"
    table_columns: list[str] = Field(default_factory=list)
    table_data: list[dict[str, Any]] | None = None
    block_ids: list[str] = Field(default_factory=list)
    image_paths: list[str] = Field(default_factory=list)
    structure_source: StructureSource = "original"

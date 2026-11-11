"""Source-preserving records shared by ingestion, chunking and retrieval."""
from typing import Any, Literal
from uuid import uuid4

from pydantic import BaseModel, Field

BlockType = Literal["heading", "paragraph", "table", "image", "list", "code", "page_header", "page_footer"]
StructureSource = Literal["original", "inferred", "unknown"]


class DocumentRecord(BaseModel):
    document_id: str = Field(default_factory=lambda: str(uuid4()))
    filename: str
    file_type: str
    source_path: str
    checksum: str
    title: str | None = None
    version: str = ""


class BlockLayout(BaseModel):
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
    document_id: str
    section_path: list[str] = Field(default_factory=list)
    content: str
    page_start: int | None = None
    page_end: int | None = None
    blocks: list[ContentBlock] = Field(default_factory=list)


class ChildChunk(BaseModel):
    chunk_id: str = Field(default_factory=lambda: str(uuid4()))
    parent_id: str
    document_id: str
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
    entities: list[str] = Field(default_factory=list)
    structure_source: StructureSource = "original"

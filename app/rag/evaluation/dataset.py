"""Versioned annotations and corpus validation; no retrieval execution here."""
import hashlib
import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator


def checksum(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalize(text: str) -> str:
    return " ".join(text.casefold().split())


class SourceAnchor(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    document_id: str = Field(min_length=1)
    source: str
    source_block_ids: list[str] = Field(min_length=1)
    section_path: list[str]
    page_number: int | None = Field(default=None, ge=1)
    page_end: int | None = Field(default=None, ge=1)
    text_quote: str = Field(min_length=1)


class Evidence(SourceAnchor):
    evidence_id: str = Field(min_length=1)
    relevance_grade: int = Field(ge=0, le=3)
    alternatives: list[SourceAnchor] = Field(default_factory=list)

    def anchors(self):
        """Alternative locations support the same fact, not extra required facts."""
        return [self, *self.alternatives]


class Question(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)
    id: str = Field(min_length=1)
    question: str = Field(min_length=1)
    category: str
    difficulty: Literal["easy", "medium", "hard"]
    answerable: bool
    expected_answer: str
    relevant_evidence: list[Evidence]
    rationale: str = Field(min_length=1)
    review_status: Literal["pending", "approved"] = "pending"
    reviewer: str | None = None

    @model_validator(mode="after")
    def check_labels(self):
        ids = [e.evidence_id for e in self.relevant_evidence]
        if len(ids) != len(set(ids)):
            raise ValueError("Duplicate evidence IDs within a question")
        if self.answerable != any(e.relevance_grade > 0 for e in self.relevant_evidence):
            raise ValueError("Answerable questions need positive evidence; unanswerable questions must have none")
        if not self.answerable and self.relevant_evidence:
            raise ValueError("Unanswerable questions must have an empty evidence list")
        if not self.question.strip():
            raise ValueError("Query cannot be blank")
        if self.review_status == "approved" and not (self.reviewer and self.reviewer.strip()):
            raise ValueError("Approved labels need an identified human reviewer")
        return self


class Dataset:
    def __init__(self, path, *, require_reviewed=False):
        self.path = Path(path).resolve()
        self.metadata_path = self.path.parent / "dataset.json"
        self.metadata = json.loads(self.metadata_path.read_text(encoding="utf-8"))
        if self.metadata["schema_version"] not in {1, 2}:
            raise ValueError("Unsupported benchmark schema version")
        self.questions = [Question.model_validate_json(line) for line in
                          self.path.read_text(encoding="utf-8").splitlines() if line.strip()]
        ids = [q.id for q in self.questions]
        if not ids or len(ids) != len(set(ids)):
            raise ValueError("Dataset must be nonempty with unique question IDs")
        self.pending_count = sum(q.review_status != "approved" for q in self.questions)
        if require_reviewed and self.pending_count:
            raise ValueError(f"{self.pending_count} questions still need human review")
        self.documents_dir = (self.path.parent / self.metadata["documents_dir"]).resolve()
        self.manifest_path = self.documents_dir.parent / "manifest.json"
        self.manifest = json.loads(self.manifest_path.read_text(encoding="utf-8"))
        self.sha256 = checksum(self.path)

    def validate_corpus(self):
        from app.rag.loader import discover_documents

        expected = {entry["file"]: entry["sha256"] for entry in self.manifest["documents"]}
        actual = {p.relative_to(self.documents_dir).as_posix(): checksum(p)
                  for p in discover_documents(self.documents_dir)}
        if actual != expected:
            raise ValueError("Benchmark corpus differs from manifest (missing, added or changed documents)")

    def validate_index(self, retriever):
        """Fail before scoring if labels are stale or a quoted source is absent."""
        if {d.document_id for d in retriever.documents} != {e["sha256"] for e in self.manifest["documents"]}:
            raise ValueError("Indexed documents do not match the benchmark corpus")
        for question in self.questions:
            for evidence in question.relevant_evidence:
                for number, anchor in enumerate(evidence.anchors()):
                    label = f"{question.id}/{evidence.evidence_id}/anchor-{number}"
                    blocks = [b for p in retriever.parents.values() if p.document_id == anchor.document_id
                              for b in p.blocks if set(b.source_block_ids or [b.block_id]) & set(anchor.source_block_ids)]
                    if not blocks or not any(normalize(anchor.text_quote) in normalize(b.text) for b in blocks):
                        raise ValueError(f"Unresolved source evidence: {label}")
                    resolved_ids = {key for b in blocks for key in (b.source_block_ids or [b.block_id])}
                    if not set(anchor.source_block_ids) <= resolved_ids:
                        raise ValueError(f"Unresolved source evidence IDs: {label}")
                    matching = [b for b in blocks if normalize(anchor.text_quote) in normalize(b.text)]
                    if not any(b.section_path == anchor.section_path and b.page_number == anchor.page_number
                               and b.page_end == anchor.page_end for b in matching):
                        raise ValueError(f"Stale evidence location: {label}")
                    source = next(d.filename for d in retriever.documents if d.document_id == anchor.document_id)
                    if anchor.source != source:
                        raise ValueError(f"Stale evidence filename: {label}")

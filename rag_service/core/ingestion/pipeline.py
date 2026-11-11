"""Document-to-chunk processing without embedding, vector stores or index publishing."""

from dataclasses import dataclass, field
import hashlib
import json
from uuid import uuid4
from pathlib import Path

from rag_service.core.ingestion.docling_parser import file_checksum
from rag_service.core.loader import discover_documents
from rag_service.core.models import ChildChunk, DocumentRecord, ParentChunk
from rag_service.core.processing.cross_page_merger import CrossPageMerger
from rag_service.core.processing.structure_recovery import StructureRecovery


@dataclass
class IngestionResult:
    documents: list[DocumentRecord] = field(default_factory=list)
    parents: list[ParentChunk] = field(default_factory=list)
    children: list[ChildChunk] = field(default_factory=list)


class IngestionPipeline:
    def __init__(self, parser, parent_chunker, child_chunker, *, cache_dir=None):
        self.parser = parser
        self.parent_chunker = parent_chunker
        self.child_chunker = child_chunker
        self.cache_dir = Path(cache_dir) if cache_dir is not None else None
        self.cache_hits = self.cache_misses = 0

    def run(
        self,
        knowledge_dir,
        *,
        files: list[Path] | None = None,
        documents: list[DocumentRecord] | None = None,
    ) -> IngestionResult:
        """Discover a directory, or reuse the facade's ordered signature file list.

        Tokenizers and effective chunk budgets are supplied through the chunkers.
        The parser retains its existing optional parsed-document/image archives.
        """
        if files is not None and documents is not None:
            raise ValueError("Provide files or versioned documents, not both")
        result = IngestionResult()
        if documents is not None:
            for document in documents:
                if (
                    not document.version_id
                    or not document.artifact_id
                    or not document.source_blob_path
                ):
                    raise ValueError(
                        "Managed ingestion requires a version, artifact and immutable source"
                    )
                if file_checksum(Path(document.source_blob_path)) != document.checksum:
                    raise ValueError(f"Immutable source changed: {document.filename}")
                cached = self._load_artifact(document)
                if cached is not None:
                    self.cache_hits += 1
                    result.documents.extend(cached.documents)
                    result.parents.extend(cached.parents)
                    result.children.extend(cached.children)
                    continue
                self.cache_misses += 1
                parsed = self.parser.parse(
                    document.source_blob_path, source_name=document.filename
                )
                if parsed.document.checksum != document.checksum:
                    raise ValueError(f"Immutable source changed: {document.filename}")
                parsed.document = document.model_copy(
                    update={"title": document.title or parsed.document.title}
                )
                parsed.blocks = [
                    block.model_copy(update={"document_id": document.document_id})
                    for block in parsed.blocks
                ]
                processed = IngestionResult()
                self._append(processed, parsed)
                self._save_artifact(document, processed)
                result.documents.extend(processed.documents)
                result.parents.extend(processed.parents)
                result.children.extend(processed.children)
            return result

        # Standalone/frozen ingestion keeps its legacy content-addressed identity.
        files = discover_documents(knowledge_dir) if files is None else files
        seen = set()
        for path in files:
            checksum = file_checksum(path)
            if checksum in seen:
                continue
            parsed = self.parser.parse(path)
            seen.add(checksum)
            self._append(result, parsed)
        return result

    def _append(self, result, parsed):
        result.documents.append(parsed.document)
        blocks = CrossPageMerger().merge(parsed.blocks)
        blocks = StructureRecovery().recover(blocks)
        parents = self.parent_chunker.split(blocks, parsed.document)
        result.parents.extend(parents)
        for parent in parents:
            result.children.extend(
                self.child_chunker.split(
                    parent,
                    parsed.document.filename,
                    parsed.document.file_type,
                )
            )

    def _load_artifact(self, document):
        if self.cache_dir is None:
            return None
        try:
            value = json.loads(
                (self.cache_dir / (document.artifact_id + ".json")).read_text(
                    encoding="utf-8"
                )
            )
            payload = value["payload"]
            digest = hashlib.sha256(
                json.dumps(
                    payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
                ).encode()
            ).hexdigest()
            if (
                value["schema_version"] != 1
                or value["sha256"] != digest
                or payload["artifact_id"] != document.artifact_id
            ):
                return None
            parents = [ParentChunk.model_validate(item) for item in payload["parents"]]
            children = [ChildChunk.model_validate(item) for item in payload["children"]]
            if any(
                item.document_id != document.document_id
                or item.version_id != document.version_id
                or item.artifact_id != document.artifact_id
                for item in [*parents, *children]
            ):
                return None
            return IngestionResult(
                [
                    document.model_copy(
                        update={"title": document.title or payload.get("title")}
                    )
                ],
                parents,
                children,
            )
        except (OSError, ValueError, KeyError, TypeError):
            return (
                None  # Disposable cache: regenerate from the verified immutable source.
            )

    def _save_artifact(self, document, result):
        if self.cache_dir is None:
            return
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        payload = dict(
            document_id=document.document_id,
            version_id=document.version_id,
            artifact_id=document.artifact_id,
            title=result.documents[0].title,
            parents=[item.model_dump(mode="json") for item in result.parents],
            children=[item.model_dump(mode="json") for item in result.children],
        )
        digest = hashlib.sha256(
            json.dumps(
                payload, sort_keys=True, ensure_ascii=False, separators=(",", ":")
            ).encode()
        ).hexdigest()
        temporary = self.cache_dir / f".{uuid4().hex}.tmp"
        try:
            temporary.write_text(
                json.dumps(
                    dict(schema_version=1, sha256=digest, payload=payload),
                    ensure_ascii=False,
                ),
                encoding="utf-8",
            )
            temporary.replace(self.cache_dir / (document.artifact_id + ".json"))
        finally:
            temporary.unlink(missing_ok=True)

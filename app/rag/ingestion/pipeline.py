"""Document-to-chunk processing without embedding, vector stores or index publishing."""
from dataclasses import dataclass, field
from pathlib import Path

from app.rag.ingestion.docling_parser import file_checksum
from app.rag.loader import discover_documents
from app.rag.models import ChildChunk, DocumentRecord, ParentChunk
from app.rag.processing.cross_page_merger import CrossPageMerger
from app.rag.processing.structure_recovery import StructureRecovery


@dataclass
class IngestionResult:
    documents: list[DocumentRecord] = field(default_factory=list)
    parents: list[ParentChunk] = field(default_factory=list)
    children: list[ChildChunk] = field(default_factory=list)


class IngestionPipeline:
    def __init__(self, parser, parent_chunker, child_chunker):
        self.parser = parser
        self.parent_chunker = parent_chunker
        self.child_chunker = child_chunker

    def run(self, knowledge_dir, *, files: list[Path] | None = None) -> IngestionResult:
        """Discover a directory, or reuse the facade's ordered signature file list.

        Tokenizers and effective chunk budgets are supplied through the chunkers.
        The parser retains its existing optional parsed-document/image archives.
        """
        files = discover_documents(knowledge_dir) if files is None else files
        result = IngestionResult()
        seen = set()
        for path in files:
            checksum = file_checksum(path)
            if checksum in seen:
                continue
            parsed = self.parser.parse(path)
            seen.add(checksum)
            result.documents.append(parsed.document)
            blocks = CrossPageMerger().merge(parsed.blocks)
            blocks = StructureRecovery().recover(blocks)
            parents = self.parent_chunker.split(blocks, parsed.document)
            result.parents.extend(parents)
            for parent in parents:
                result.children.extend(self.child_chunker.split(
                    parent, parsed.document.filename, parsed.document.file_type,
                ))
        return result

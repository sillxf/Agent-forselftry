"""Small retrieval units retain their parents, evidence and table column names."""
import re
from uuid import NAMESPACE_URL, uuid5

from app.rag.chunking.text import count_tokens, split_text
from app.rag.models import ChildChunk, ContentBlock, ParentChunk

ENTITY_PATTERN = re.compile(
    r"CVE-\d{4}-\d{4,7}|(?:\d{1,3}\.){3}\d{1,3}|\b[0-9a-f]{32,128}\b|"
    r"\bT\d{4}(?:\.\d{3})?\b|\b[A-Z]+[-_]?\d{3,}\b", re.IGNORECASE,
)


class ChildChunker:
    def __init__(self, tokenizer, max_tokens: int = 400, overlap_tokens: int = 60):
        if max_tokens < 8 or not 0 <= overlap_tokens < max_tokens:
            raise ValueError("Require max_tokens >= 8 and 0 <= overlap_tokens < max_tokens")
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens
        self.overlap_tokens = overlap_tokens

    def split(self, parent: ParentChunk, source_name: str, file_type: str = "") -> list[ChildChunk]:
        chunks = []
        prefix = " > ".join([source_name, *parent.section_path])
        # Reserve at least half of the budget for source text, even with long titles.
        prefix = next(split_text(prefix, self.tokenizer, self.max_tokens // 2), "")
        groups = []
        # Adjacent text blocks can share a child; table/image evidence is kept distinct.
        for block in parent.blocks:
            if block.block_type in {"table", "image", "code"}:
                groups.append([block])
            elif groups and groups[-1][-1].block_type not in {"table", "image", "code"}:
                groups[-1].append(block)
            else:
                groups.append([block])
        if not groups:
            groups = [[ContentBlock(document_id=parent.document_id, block_type="paragraph", text=parent.content,
                                    page_number=parent.page_start, page_end=parent.page_end)]]
        for group in groups:
            kind = group[0].block_type if len(group) == 1 else "text"
            context = "\n".join(filter(None, [prefix, group[0].caption]))
            context = next(split_text(context, self.tokenizer, self.max_tokens // 2), "")
            budget = self.max_tokens - count_tokens(self.tokenizer, context + "\n") - 2
            overlap = min(self.overlap_tokens, budget - 1)
            texts = ["\n\n".join(b.text for b in group if b.text)]
            if kind == "table" and group[0].table_data:
                # Each row repeats its keys; a match cannot lose its column meanings.
                texts = ["\n".join(f"{key}: {value}" for key, value in row.items())
                         for row in group[0].table_data]
            for row_index, text in enumerate(texts):
                if not text.strip():
                    continue
                for piece in split_text(text, self.tokenizer, budget, overlap):
                    search_text = f"{context}\n{piece}"
                    pages = [b.page_number for b in group if b.page_number is not None]
                    ends = [b.page_end or b.page_number for b in group if b.page_number is not None]
                    chunks.append(ChildChunk(
                        chunk_id=str(uuid5(NAMESPACE_URL, f"{parent.parent_id}:child:{len(chunks)}")),
                        parent_id=parent.parent_id, document_id=parent.document_id,
                        source_name=source_name, file_type=file_type, content=piece, search_text=search_text,
                        page_start=min(pages) if pages else None, page_end=max(ends) if ends else None,
                        section_path=parent.section_path, chunk_type=kind,
                        table_columns=group[0].table_columns if kind == "table" else [],
                        table_data=[group[0].table_data[row_index]] if kind == "table" and group[0].table_data else None,
                        block_ids=list(dict.fromkeys(b.block_id for b in group)),
                        image_paths=[b.image_path for b in group if b.image_path],
                        entities=list(dict.fromkeys(m.group() for m in ENTITY_PATTERN.finditer(piece))),
                        structure_source=("inferred" if any(b.structure_source == "inferred" for b in group)
                                          else "unknown" if any(b.structure_source == "unknown" for b in group)
                                          else "original"),
                    ))
        return chunks

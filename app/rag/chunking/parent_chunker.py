"""Build bounded, section-aware parents; page breaks are not section breaks."""
from uuid import NAMESPACE_URL, uuid5

from app.rag.chunking.text import count_tokens, split_text
from app.rag.models import ContentBlock, DocumentRecord, ParentChunk


class ParentChunker:
    def __init__(self, tokenizer, max_tokens: int = 1600):
        if max_tokens <= 0:
            raise ValueError("max_tokens must be positive")
        self.tokenizer = tokenizer
        self.max_tokens = max_tokens

    def split(self, blocks: list[ContentBlock], document: DocumentRecord) -> list[ParentChunk]:
        parents = []
        current = []

        def flush():
            if not current:
                return
            pages = [b.page_number for b in current if b.page_number is not None]
            ends = [b.page_end or b.page_number for b in current if b.page_number is not None]
            parents.append(ParentChunk(
                parent_id=str(uuid5(NAMESPACE_URL, f"{document.document_id}:parent:{len(parents)}")),
                document_id=document.document_id,
                section_path=current[0].section_path,
                content="\n\n".join(b.text for b in current if b.text),
                page_start=min(pages) if pages else None,
                page_end=max(ends) if ends else None,
                blocks=list(current),
            ))
            current.clear()

        for block in blocks:
            if not block.text.strip() and block.block_type != "image":
                continue
            if current and block.section_path != current[0].section_path:
                flush()
            units = [block]
            if block.block_type == "table" and block.table_data:
                # Large tables are grouped by whole rows, not arbitrary character cuts.
                units, rows = [], []
                texts = [block.caption] if block.caption else []
                for row in block.table_data:
                    row_text = "\n".join(f"{key}: {value}" for key, value in row.items())
                    if rows and count_tokens(self.tokenizer, "\n\n".join([*texts, row_text])) > self.max_tokens:
                        units.append(block.model_copy(update={"text": "\n\n".join(texts), "table_data": rows}))
                        rows, texts = [], [block.caption] if block.caption else []
                    rows.append(row)
                    texts.append(row_text)
                if rows:
                    units.append(block.model_copy(update={"text": "\n\n".join(texts), "table_data": rows}))
            elif block.block_type != "table":
                units = [block.model_copy(update={"text": piece})
                         for piece in split_text(block.text, self.tokenizer, self.max_tokens)]
            for unit in units:
                candidate = "\n\n".join([*(b.text for b in current), unit.text])
                if current and count_tokens(self.tokenizer, candidate) > self.max_tokens:
                    flush()
                current.append(unit)
        flush()
        return parents

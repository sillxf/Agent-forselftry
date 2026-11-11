"""Deterministic local providers for the single bounded service smoke check."""

import hashlib
from pathlib import Path
import numpy as np
from app.knowledge.models import ContentBlock, DocumentRecord, ParsedDocument
from app.ingestion.docling_parser import file_checksum


class Tokenizer:
    def encode(self, text, add_special_tokens=False):
        return list(text)

    def num_special_tokens_to_add(self, pair=False):
        return 0


class FakeEmbedding:
    def __init__(self, config):
        self.config = config
        self.calls = []

    def tokenizer_and_limit(self):
        return Tokenizer(), 8192

    def count_tokens(self, text):
        return len(Tokenizer().encode(text))

    def embed_documents(self, texts):
        self.calls.append(("documents", texts))
        return self.encode(texts)

    def embed_query(self, texts):
        self.calls.append(("query", texts))
        return self.encode(texts)

    def encode(self, texts):
        result = np.zeros(
            (len(texts), self.config.get("dimension") or 32), dtype="float32"
        )
        for i, text in enumerate(texts):
            for word in text.lower().split():
                result[
                    i,
                    int(hashlib.sha256(word.encode()).hexdigest()[:8], 16)
                    % result.shape[1],
                ] += 1
        return result


class Parser:
    ocr_enabled = False

    def parse(self, path, source_name=None):
        path = Path(path)
        text = path.read_text(encoding="utf-8")
        checksum = file_checksum(path)
        return ParsedDocument(
            document=DocumentRecord(
                filename=source_name or path.name,
                file_type="md",
                source_path=str(path),
                checksum=checksum,
            ),
            blocks=[
                ContentBlock(
                    document_id=checksum,
                    block_type="paragraph",
                    text=text,
                    page_number=1,
                )
            ],
            markdown=text,
        )

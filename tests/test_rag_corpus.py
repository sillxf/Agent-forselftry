"""Parse checked-in inputs; opt-in PDF/OCR tests may download models on first use."""
import hashlib
import json
from pathlib import Path

import pytest

from app.rag.ingestion.docling_parser import DoclingParser, is_image_only_pdf
from app.rag.processing.cross_page_merger import CrossPageMerger
from app.rag.processing.structure_recovery import StructureRecovery

ROOT = Path(__file__).parent / "fixtures/rag_documents"
DOCUMENTS = json.loads((ROOT / "manifest.json").read_text(encoding="utf-8"))["documents"]


@pytest.fixture(scope="module")
def corpus_parser(tmp_path_factory):
    return DoclingParser(image_dir=tmp_path_factory.mktemp("corpus-images"))


def test_corpus_manifest_is_reproducible():
    assert len(DOCUMENTS) == 15
    for entry in DOCUMENTS:
        path = ROOT / entry["file"]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == entry["sha256"], entry["file"]
        assert entry["purpose"] and entry["expected"] and entry["origin"]["kind"]
        if entry["format"] == "pdf":
            assert is_image_only_pdf(path) == ("image_only_pdf" in entry["purpose"])


@pytest.mark.parametrize("entry", [pytest.param(entry, marks=pytest.mark.rag_models) if entry["requires_models"] else entry
                                  for entry in DOCUMENTS], ids=[e["file"] for e in DOCUMENTS])
def test_document_corpus(entry, corpus_parser):
    parsed = corpus_parser.parse(ROOT / entry["file"])
    merged = CrossPageMerger().merge(parsed.blocks)
    recovered = StructureRecovery().recover(merged)
    expected = entry["expected"]
    text = " ".join(" ".join(block.text.split()) for block in recovered).casefold()
    headings = [block.text for block in recovered if block.block_type == "heading"]
    for phrase in expected.get("contains", []):
        assert phrase.casefold() in text
    for phrase in expected.get("excludes", []):
        assert phrase.casefold() not in text
    for heading in expected.get("inferred_headings", []):
        assert any(b.text == heading and b.block_type == "heading" and b.structure_source == "inferred" for b in recovered)
    for heading in expected.get("headings", []):
        assert heading in headings
    for step in expected.get("not_headings", []):
        assert step not in headings
    if "pages" in expected:
        assert sorted({b.page_number for b in parsed.blocks if b.page_number}) == expected["pages"]
    tables = [b for b in merged if b.block_type == "table"]
    if "table_count" in expected:
        assert len(tables) == expected["table_count"]
    if "table_min_count" in expected:
        assert len(tables) >= expected["table_min_count"]
    for value in expected.get("table_values", []):
        assert any(value in [str(v) for row in (table.table_data or []) for v in row.values()] for table in tables)
    for occurrence in expected.get("layout_occurrences", []):
        blocks = [b for b in parsed.blocks if b.text == occurrence["text"]]
        assert [b.layout.font_size for b in blocks] == occurrence["font_sizes"]
        assert [b.layout.bold for b in blocks] == occurrence["bold"]
    if "merged_text" in expected:
        assert any(b.text == expected["merged_text"] for b in merged)
    if "merged_pages" in expected:
        # Docling can already return a logical block with provenance on both pages.
        assert any([b.page_number, b.page_end] == expected["merged_pages"]
                   and ("merged_type" not in expected or b.block_type == expected["merged_type"]) for b in merged)
        assert all(len(b.source_block_ids) >= 2 for b in merged if b.merge_reason)
    if "merge_count" in expected:
        assert sum(b.merge_reason is not None for b in merged) == expected["merge_count"]
    if "picture_min_count" in expected:
        assert sum(b.block_type == "image" for b in parsed.blocks) >= expected["picture_min_count"]
    if expected.get("source_image"):
        source = parsed.blocks[0]
        assert source.block_type == "image" and source.image_path
        assert source.caption is None and source.heading_level is None and source.list_marker is None
        assert source.structure_source == "unknown"

"""PDF regressions use a real frozen Docling output, plus small boundary cases."""
import json
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.rag.ingestion.docling_parser import DoclingParser
from app.rag.models import BlockLayout, ContentBlock
from app.rag.processing.cross_page_merger import CrossPageMerger
from app.rag.processing.structure_recovery import StructureRecovery

ROOT = Path(__file__).parent
PDF = ROOT / "rag_benchmark/documents/nist_sp80061r3_pp10-12.pdf"
FIXTURE = ROOT / "fixtures/rag_structure"


def recover_nist(parser):
    parsed = parser.parse(PDF)
    blocks = StructureRecovery().recover(CrossPageMerger().merge(parsed.blocks))
    headings = {b.text: b for b in blocks if b.block_type == "heading"}
    assert "1. Introduction" in headings
    assert headings["1.1. Purpose and Scope"].heading_level == 2
    assert headings["1.1. Purpose and Scope"].structure_source == "inferred"
    assert headings["2.1. Incident Response Life Cycle Model"].heading_level == 2
    assert headings["2.1. Incident Response Life Cycle Model"].structure_source == "original"
    assert "Containment" not in headings
    assert "A cybersecurity incident (or simply incident) is" not in headings
    assert all("Containment" not in b.section_path for b in blocks)
    purpose = next(b for b in blocks if b.text.startswith("This publication seeks"))
    assert purpose.section_path == ["1. Introduction", "1.1. Purpose and Scope"]
    lessons = next(b for b in blocks if "The lessons learned during incident response" in b.text)
    assert lessons.section_path == ["2. Incident Response as Part of Cybersecurity Risk Management", "2.1. Incident Response Life Cycle Model"]
    assert next(b for b in blocks if b.text == "Containment").layout.container_type == "picture"
    assert any(b.page_number == 1 and b.page_end == 2 and "governance efforts" in b.text for b in blocks)
    return blocks


def test_nist_structure_from_real_docling_output_without_model_downloads():
    from docling_core.types.doc import DoclingDocument
    from docling_core.types.doc.page import PdfTextCell, TextCell
    doc = DoclingDocument.model_validate_json((FIXTURE / "nist_docling.json").read_text(encoding="utf8"))
    cells = json.loads((FIXTURE / "nist_page_cells.json").read_text(encoding="utf8"))
    result = SimpleNamespace(status="success", document=doc,
        pages=[SimpleNamespace(page_no=int(number), cells=[(TextCell if c["from_ocr"] else PdfTextCell).model_validate(c) for c in records])
               for number, records in cells.items()])
    converter = SimpleNamespace(convert=lambda path: result)
    recover_nist(DoclingParser(converter=converter))


@pytest.mark.rag_models
def test_nist_structure_from_live_pdf_conversion():
    recover_nist(DoclingParser())


def block(text, kind="paragraph", **kwargs):
    return ContentBlock(document_id="manual", block_type=kind, text=text, **kwargs)


@pytest.mark.parametrize("layout", [BlockLayout(container_type="picture"),
    BlockLayout(container_type="table"), BlockLayout(source_label="caption", bold=True)])
def test_figure_labels_and_table_captions_never_become_topic_headings(layout):
    result = StructureRecovery().recover([
        block("Response", "heading", heading_level=1, section_path=["Response"]),
        block("Containment", layout=layout), block("Continue the actual response process.")])
    assert result[1].block_type == "paragraph"
    assert result[-1].section_path == ["Response"]


def test_pdf_numbered_headers_body_numbers_and_column_positions():
    blocks = [block("Overview", "heading", heading_level=1, section_path=["Overview"]),
        block("Investigative details", "list", list_marker="1.1.", layout=BlockLayout(bold=True, indent=300)),
        block("The evidence is recorded in the following paragraphs and can be independently checked.", layout=BlockLayout(indent=300)),
        block("Check the logs", "list", list_marker="1.", layout=BlockLayout(bold=True, indent=72)),
        block("Other column evidence continues.", layout=BlockLayout(indent=300))]
    result = StructureRecovery().recover(blocks)
    assert result[1].block_type == "heading"
    assert result[3].block_type == "list"  # Bold operational numbering is not a chapter.
    assert result[-1].section_path == result[2].section_path
    assert result[1].heading_level == 3  # Inferred numbering is relative to the native chapter.
    numbered = StructureRecovery().recover([
        block("2. Risk", "heading", heading_level=1, section_path=["2. Risk"]),
        block("Evidence", "list", list_marker="2.1.", layout=BlockLayout(bold=True)),
        block("These paragraphs describe enough detail to support the recovered heading.")])
    assert numbered[1].heading_level == 2
    assert numbered[-1].section_path == ["2. Risk", "2.1. Evidence"]


def test_native_pdf_figure_headers_are_rejected_before_updating_paths():
    from docling_core.types.doc import DoclingDocument
    from docling_core.types.doc.labels import DocItemLabel
    doc = DoclingDocument(name="diagram")
    doc.add_heading(text="What security is", level=1)
    picture = doc.add_picture()
    doc.add_heading(text="Containment", level=1, parent=picture)
    doc.add_text(label=DocItemLabel.TEXT, text="Actual chapter body, outside the diagram.")
    result = SimpleNamespace(status="success", document=doc)
    parser = DoclingParser(converter=SimpleNamespace(convert=lambda path: result))
    blocks = StructureRecovery().recover(parser.parse(PDF).blocks)
    assert blocks[-1].section_path == ["What security is"]
    assert next(b for b in blocks if b.text=="Containment" and b.block_type!="image").block_type == "paragraph"


def check_two_columns(parser):
    parsed = parser.parse(FIXTURE / "two_column.pdf")
    blocks = StructureRecovery().recover(CrossPageMerger().merge(parsed.blocks))
    left = next(b for b in blocks if b.text.startswith("Repeated authentication"))
    right = next(b for b in blocks if b.text.startswith("Containment requires"))
    assert left.section_path == ["1. Detection"]
    assert right.section_path == ["2. Response"]
    assert left.layout.indent < right.layout.indent
    step = next(b for b in blocks if "Check firewall configuration" in b.text)
    assert step.block_type == "list"
    assert step.section_path == ["1. Detection"]


def test_actual_two_column_docling_order_is_repaired_without_models():
    from docling_core.types.doc import DoclingDocument
    from docling_core.types.doc.page import PdfTextCell, TextCell
    doc = DoclingDocument.model_validate_json((FIXTURE / "two_column_docling.json").read_text(encoding="utf8"))
    cells = json.loads((FIXTURE / "two_column_page_cells.json").read_text(encoding="utf8"))
    result = SimpleNamespace(status="success",document=doc,
        pages=[SimpleNamespace(page_no=int(n),cells=[(TextCell if c["from_ocr"] else PdfTextCell).model_validate(c) for c in entries]) for n,entries in cells.items()])
    check_two_columns(DoclingParser(converter=SimpleNamespace(convert=lambda path: result)))
    # A full-width body below aligned headers is ambiguous, not a two-column repair.
    from app.rag.ingestion.pdf_order import order_pdf_columns
    doc.texts[3].prov[0].bbox.r = 540
    original = list(doc.iterate_items(traverse_pictures=True))
    assert order_pdf_columns(original, doc) == original


@pytest.mark.rag_models
def test_live_two_column_pdf_keeps_section_bodies_with_their_own_headers():
    check_two_columns(DoclingParser())

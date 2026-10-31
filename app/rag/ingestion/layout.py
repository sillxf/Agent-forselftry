"""Keep available source layout signals; do not invent missing font measurements."""
from collections import Counter
from difflib import SequenceMatcher
from pathlib import Path
from statistics import median

from app.rag.models import BlockLayout


def docx_layouts(path: Path, items) -> dict[str, BlockLayout]:
    if path.suffix.lower() != ".docx":
        return {}
    from docx import Document

    paragraphs, layouts = [], []
    for paragraph in Document(path).paragraphs:
        runs = [run for run in paragraph.runs if run.text.strip()]
        sizes = [run.font.size.pt for run in runs if run.font.size is not None]
        if not sizes and paragraph.style.font.size is not None:
            sizes = [paragraph.style.font.size.pt]
        indent = paragraph.paragraph_format.left_indent
        if not paragraph.text.strip():
            continue
        paragraphs.append(paragraph.text.strip())
        layouts.append(BlockLayout(
            font_size=median(sizes) if sizes else None,
            bold=bool(runs) and all(run.bold if run.bold is not None else paragraph.style.font.bold for run in runs),
            indent=indent.pt if indent is not None else None,
        ))
    text_items = [item for item, _ in items if getattr(item, "text", "").strip()]
    texts = [item.text.strip() for item in text_items]
    source_counts, item_counts = Counter(paragraphs), Counter(texts)
    matched = {}
    # Align source occurrences in reading order, rather than overwriting duplicate text keys.
    for match in SequenceMatcher(None, paragraphs, texts, autojunk=False).get_matching_blocks():
        for offset in range(match.size):
            source_index, item_index = match.a + offset, match.b + offset
            text = paragraphs[source_index]
            if source_counts[text] == item_counts[text]:
                matched[text_items[item_index].self_ref] = layouts[source_index]
    return matched


def item_layout(item, document, pages) -> BlockLayout:
    formatting = getattr(item, "formatting", None)
    layout = BlockLayout(bold=bool(formatting and formatting.bold))
    provenance = getattr(item, "prov", [])
    if not provenance:
        return layout
    prov = provenance[0]
    page = getattr(document, "pages", {}).get(prov.page_no)
    bbox = getattr(prov, "bbox", None)
    if page is None or bbox is None:
        return layout
    box = bbox.to_top_left_origin(page_height=page.size.height)
    layout.top, layout.bottom = box.t, box.b
    layout.indent, layout.page_height = box.l, page.size.height
    heights, fonts = [], []
    for cell in pages.get(prov.page_no, []):
        cell_box = cell.rect.to_bounding_box().to_top_left_origin(page_height=page.size.height)
        x, y = (cell_box.l + cell_box.r) / 2, (cell_box.t + cell_box.b) / 2
        if box.l <= x <= box.r and box.t <= y <= box.b:
            heights.append(cell_box.height)
            fonts.append(getattr(cell, "font_name", "").lower())
    if heights:
        layout.line_height = median(heights)
    if fonts:
        layout.bold = layout.bold or all("bold" in font or "demi" in font for font in fonts)
    return layout

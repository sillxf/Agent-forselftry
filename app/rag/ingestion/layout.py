"""Keep available source layout signals; do not invent missing font measurements."""
from pathlib import Path
from statistics import median

from app.rag.models import BlockLayout


def docx_layouts(path: Path) -> dict[str, BlockLayout]:
    if path.suffix.lower() != ".docx":
        return {}
    from docx import Document

    layouts = {}
    for paragraph in Document(path).paragraphs:
        runs = [run for run in paragraph.runs if run.text.strip()]
        sizes = [run.font.size.pt for run in runs if run.font.size is not None]
        if not sizes and paragraph.style.font.size is not None:
            sizes = [paragraph.style.font.size.pt]
        indent = paragraph.paragraph_format.left_indent
        layouts[paragraph.text.strip()] = BlockLayout(
            font_size=median(sizes) if sizes else None,
            bold=bool(runs) and all(run.bold if run.bold is not None else paragraph.style.font.bold for run in runs),
            indent=indent.pt if indent is not None else None,
        )
    return layouts


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

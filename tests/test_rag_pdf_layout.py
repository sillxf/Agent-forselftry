"""PDF layout reuse must preserve geometry, fonts and untouched reading order."""
from types import SimpleNamespace
from unittest.mock import Mock

from app.rag.ingestion.layout import item_layout, page_cell_geometry
from app.rag.ingestion.pdf_order import order_pdf_columns
from app.rag.models import BlockLayout


def bounding_box(left, top, right, bottom):
    box = SimpleNamespace(l=left, t=top, r=right, b=bottom, height=bottom - top)
    box.to_top_left_origin = Mock(return_value=box)
    return box


def test_cell_geometry_is_computed_once_and_shared_between_items():
    boxes = [bounding_box(0, 0, 10, 10), bounding_box(10, 10, 20, 30),
             bounding_box(100, 0, 110, 10)]
    cells = [SimpleNamespace(rect=SimpleNamespace(to_bounding_box=Mock(return_value=box)),
                             font_name=font)
             for box, font in zip(boxes, ["Arial-Bold", "Arial-Demi", "Arial"])]
    doc = SimpleNamespace(pages={1: SimpleNamespace(size=SimpleNamespace(height=1000))})
    geometry = page_cell_geometry(doc, [SimpleNamespace(page_no=1, cells=cells)])
    expected = [
        BlockLayout(source_label="text", top=0, bottom=35, indent=0, page_height=1000,
                    line_height=15, bold=True),
        BlockLayout(source_label="text", top=0, bottom=10, indent=0, page_height=1000,
                    line_height=10, bold=True),
        BlockLayout(source_label="text", top=0, bottom=10, indent=30, page_height=1000),
        BlockLayout(source_label="text", top=0, bottom=35, indent=0, page_height=1000,
                    line_height=10, bold=False),
    ]
    for box, layout in zip([bounding_box(0, 0, 20, 35), bounding_box(0, 0, 10, 10),
                            bounding_box(30, 0, 40, 10), bounding_box(0, 0, 110, 35)], expected):
        item = SimpleNamespace(label="text", prov=[SimpleNamespace(page_no=1, bbox=box)])
        assert item_layout(item, doc, geometry) == layout
    for cell, box in zip(cells, boxes):
        cell.rect.to_bounding_box.assert_called_once_with()
        box.to_top_left_origin.assert_called_once_with(page_height=1000)


def test_pdf_order_groups_items_once_and_leaves_noncolumn_content_in_place():
    class CountingItems(list):
        iterations = 0

        def __iter__(self):
            self.iterations += 1
            return super().__iter__()

    pages = {number: SimpleNamespace(size=SimpleNamespace(height=1000)) for number in range(1, 51)}
    items = CountingItems((SimpleNamespace(label="text", prov=[SimpleNamespace(
        page_no=number, bbox=bounding_box(0, 0, 100, 10))]), 1) for number in pages)
    # No provenance, multiple pages and furniture remain in their original slots.
    items.insert(2, (SimpleNamespace(label="text", prov=[]), 1))
    items.insert(3, (SimpleNamespace(label="table", prov=[SimpleNamespace(page_no=1),
                                                         SimpleNamespace(page_no=2)]), 1))
    items.insert(4, (SimpleNamespace(label="page_header", prov=[SimpleNamespace(page_no=1)]), 1))
    assert order_pdf_columns(items, SimpleNamespace(pages=pages)) == items
    assert items.iterations == 2  # One output copy, one grouping pass, independent of page count.

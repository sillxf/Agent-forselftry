"""Repair a bounded PDF reading-order defect: two aligned independent text columns."""
from itertools import combinations

from app.rag.ingestion.layout import item_layout


def order_pdf_columns(items, document):
    """Use disjoint body bounds, not document names or a global x/y sort.

    A pair of aligned section headers must have body text on BOTH sides of a real
    gutter. Spanning body text, tables/pictures or ambiguous/more complex layouts
    stay in Docling order. Headers/footers and content above the columns stay put.
    """
    output = list(items)
    pages = getattr(document, "pages", {})
    for page_no, page in pages.items():
        entries = []
        for index, (item, _) in enumerate(items):
            prov = getattr(item, "prov", [])
            label = getattr(item.label, "value", item.label)
            if len(prov) != 1 or prov[0].page_no != page_no or label in {"page_header", "page_footer"}:
                continue
            box = prov[0].bbox.to_top_left_origin(page_height=page.size.height)
            if item_layout(item, document, {}).container_type:
                continue
            entries.append((index, item, label, box))
        headers = [e for e in entries if e[2] == "section_header"]
        for one, two in combinations(headers, 2):
            left, right = sorted((one, two), key=lambda e:e[3].l)
            if abs(left[3].t-right[3].t) > max(left[3].height,right[3].height) or right[3].l-left[3].r < 18:
                continue
            top = min(left[3].t,right[3].t)
            region = [e for e in entries if e[3].t >= top-1]
            if any(e[2] in {"picture", "table"} for e in region):
                continue
            columns = [[e for e in region if (e[3].l >= right[3].l-8) == side] for side in (False,True)]
            if any(not any(e[2] in {"text","paragraph","list_item"} for e in column) for column in columns):
                continue
            if max(e[3].r for e in columns[0])+18 > min(e[3].l for e in columns[1]):
                continue
            ordered = [e for column in columns for e in sorted(column,key=lambda e:(e[3].t,e[0]))]
            for position, entry in zip(sorted(e[0] for e in region), ordered):
                output[position] = items[entry[0]]
            break
    return output

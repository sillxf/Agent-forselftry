# Offline PDF structure regression

`nist_docling.json` is the actual Docling output for the unchanged 3-page excerpt
in `tests/rag_benchmark/documents/nist_sp80061r3_pp10-12.pdf` (SHA-256
`dc95e150e756524e3bc38e81b5be7e2e912135c1633aea9f885667fe521e4830`).
Only the embedded picture PNG was removed (`image: null`); original text, labels,
references, bounds, ordering and hierarchy were not corrected in this fixture.
`nist_page_cells.json` contains original Docling textline cells/fonts retained with
`PdfPipelineOptions.generate_parsed_pages=True`. It is not hand-authored layout.

The normal test suite loads both files through Docling's actual document/cell
models and the production parser, merger and structure recovery, without loading
PDF/OCR models. The opt-in `--rag-models` suite also reparses the original PDF.
This is a regression input, not an additional benchmark corpus document.

Attribution: NIST SP 800-61 Rev. 3 (April 2025), physical PDF pages 10–12,
printed pages 2–4, US government publication. Source provenance is retained in the
benchmark corpus manifest. No source PDF text or diagram was edited.

Captured with docling 2.145.0 / docling-core 2.105.0.

## Two-column regression

`two_column.pdf` is a synthetic, deterministic one-page PDF authored for this test.
Run `build_two_column.py` with reportlab to regenerate it; reportlab is not a test
runtime dependency. Its rendered layout was visually inspected. The adjacent raw
Docling document and page cells preserve the actual erroneous order: both column
headers precede the left-column body. No raw output ordering was manually fixed.
Both an offline replay and opt-in live parse check that Detection/Response bodies
stay under their own headings and numbered operational steps remain list items.
The generic repair only applies to two aligned, disjoint text columns with a gutter;
complex mixed figure/table layouts deliberately remain in upstream reading order.

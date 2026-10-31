# v1.1 RAG document regression corpus

This is a structural regression corpus, **not** a retrieval benchmark. It contains
15 checked-in documents: four external-derived inputs and eleven generated boundary
fixtures. `manifest.json` records each file's SHA-256, source/version, purpose, model
requirement and explicit expected behaviour. There are 32 expectation groups; these
are assertions about documents, not 32 independent test cases.

## Inputs and acceptance checks

| File | Origin | Checks |
| --- | --- | --- |
| `pdf/text_based/nist_sp80061r3_pp10-12.pdf` | NIST SP 800-61 Rev. 3 | Real security text and page provenance |
| `pdf/cross_page/sentence_continuation.pdf` | Generated | Continuous sentence, pages 1–2, removal of repeated page furniture |
| `pdf/tables/continued_rules.pdf` | Generated | One continued table, repeated header, all four rule IDs, pages 1–2 |
| `pdf/scanned/incident_note.pdf` | Generated raster-only PDF | No native text; OCR must recover both expected lines |
| `pdf/cross_page/figure_interrupts_text.pdf` | Generated | Preserve picture/text; records a known non-adjacent merge limitation |
| `docx/duplicate_paragraphs.docx` | Generated | Identical text retains its own 18pt/bold and 10pt/non-bold layout |
| `docx/numbered_steps.docx` | Generated | English/Chinese operational steps are not inferred headings |
| `docx/no_heading.docx` | Generated | Layout-derived headings are marked `inferred` |
| `docx/cross_page_lists.docx` | Generated | Explicit page break and independent sections/lists remain separate |
| `xlsx/xlsx_01.xlsx` | Docling upstream fixture | Six tables, sheet content and column labels |
| `xlsx/xlsx_05_table_with_title.xlsx` | Docling upstream fixture | Two tables, title/content preservation |
| `pptx/powerpoint_sample.pptx` | Docling upstream fixture | Three slides and table preservation |
| `images/no_ocr.png` | Generated | Source image exists even without OCR text; clean metadata |
| `images/ocr_note.png` | Generated | Expected OCR text and clean source-image metadata |
| `images/multi_region_ocr.png` | Generated | All three OCR regions and clean source-image metadata |

A native Docling paragraph/table can already span two pages. Tests accept that, or a
merge performed by `CrossPageMerger`; new merges must retain multiple source block IDs.
Missing-marker continuity and repeated body-text boundaries also have focused block
contract tests in `tests/test_rag_processing.py`.

## Run

Normal regression tests parse Office/HTML/Markdown inputs without model downloads:

```powershell
python -m pip install -r requirements.txt
python -m pip check
python -m pytest -q
```

PDF/image cases are explicitly marked `rag_models`: eight are skipped by the normal
command. Run the complete corpus and all other tests with:

```powershell
python -m pytest -q --rag-models --junitxml=test-results/with-models.xml
```

The first model-enabled run requires network access for Docling/OCR artifacts. Once
cached, use `HF_HUB_OFFLINE=1` and `TRANSFORMERS_OFFLINE=1` for an offline rerun. Tests
reuse a parser in a temporary image directory and do not require an LLM, embedding
API, personal documents or a network-mounted corpus.

PDF routing checks run without models: only a PDF with no native text on **any** page
uses full-page OCR. Text-bearing and mixed PDFs retain Docling's default PDF-aware OCR.
Image inputs use full-page OCR. This avoids forcing native text PDFs through OCR.

The GitHub Actions workflow runs the default suite and saves JUnit XML. Use its manual
`rag_models` input for full PDF/OCR validation. A workflow definition alone does not
mean remote CI has passed.

## Sources, licenses and regeneration

- NIST source: `https://nvlpubs.nist.gov/nistpubs/SpecialPublications/NIST.SP.800-61r3.pdf`.
  The checked-in file is **physical source pages 10–12**, renumbered as output pages
  1–3, not the full publication. The manifest retains the original source checksum
  and attribution. This is a U.S. government NIST publication.
- XLSX/PPTX sources: the Docling repository at commit
  `764b5d4dc22b03ea87afd4c2207f510300b27a5b`. Exact raw URLs are in the manifest;
  upstream MIT attribution is retained in `DOCLING_LICENSE.txt`.
- Generated fixtures: `scripts/build_rag_corpus.py`, using only synthetic SOC text,
  primitive shapes and explicit formatting. They contain no credentials or case data.

Regenerate from the repository root (extra dependencies are only for regeneration):

```powershell
python -m pip install -r requirements-corpus.txt
python scripts/build_rag_corpus.py --download
# Optional network proxy:
python scripts/build_rag_corpus.py --download --proxy http://127.0.0.1:7897
```

Without `--download`, the generator reuses the external files and the full NIST PDF
in the system temporary directory. Inputs are pinned/hashed; generated DOCX ZIP
timestamps and ReportLab metadata are deterministic. Generator library changes can
change binary hashes, so regenerate/review the manifest together with fixture changes.
Ordinary test runs never regenerate or download source documents.

## Deliberately not claimed

- A picture between page continuations can still interrupt merging; the corpus records
  this rather than treating text preservation as proof of a successful merge.
- DOCX page breaks are source instructions, not rendered page provenance. The list
  fixture protects section separation; missing-marker cross-page behaviour is also
  checked directly at the block contract.
- OCR coverage is a few clear English samples, not a guarantee for degraded scans,
  arbitrary Chinese scans or mixed-document OCR accuracy.
- No Recall@K/MRR/NDCG labels, reranker, VLM, image embeddings or index replacement
  are introduced here. Those belong to later versions.

# AI-SecOps-Agent

An AI-assisted security alert investigation system.

## Current features

- Security alert data model
- List and filter alerts by severity
- Retrieve a single alert by ID
- HTTP API tests

## Setup

Create and activate a Python 3.11+ virtual environment (validated with Python 3.13), then run:

    python -m pip install -r requirements.txt

## Start the application

    uvicorn app.main:app --reload

## Run tests

    python -m pytest -q

PDF/OCR corpus tests are opt-in (models may download on first use):

    python -m pytest -q --rag-models

## API documentation

Open http://127.0.0.1:8000/docs

## Roadmap

- Alert normalization and deduplication
- Asset and event investigation tools
- Retrieval-augmented generation
- Agent tool calling
- Workflow and ReAct comparison
- Evaluation and observability

## RAG Pipeline

1. Docling parses Markdown, PDF, DOCX, XLSX, PPTX, HTML and images into shared
   document/block records, retaining headings, available page numbers, tables and pictures.
2. Cross-page processing removes page furniture and joins continued paragraphs, tables
   and lists; structure recovery adds rule/layout-based section paths when headings are missing.
3. Section-aware parents provide context; smaller overlapping children provide retrieval
   units. Chunking uses the embedding tokenizer and counts source/section prefixes in the
   model's input budget. Tables retain column/value pairs and are grouped by whole rows.
4. Normalized embeddings use FAISS cosine retrieval. BM25+ preserves exact security
   identifiers and uses basic Chinese character/bigram tokens. RRF merges both rankings.
5. Search restores parent context and keeps source names, document/parent/chunk IDs,
   section paths, page ranges and picture paths.

`KnowledgeRetriever(build=True/False)`, `build_index()`, `search(query, k=2)` and
`/knowledge/search?q=...&k=3` remain available. Results retain `source` and `content`;
`content` is now the parent context and `chunk_content` is the matched fragment.
`matched_page_start/end` cover the child's source blocks; pageless formats use null.
The investigation prompt retains source identities and treats retrieved text as
untrusted reference data. Its analysis output schema is unchanged.

### Configuration and indexing

Install `requirements.txt`; see `.env.example` for RAG settings. Relative paths resolve
against the repository. The default embedding remains `all-MiniLM-L6-v2`; set
`RAG_EMBEDDING_MODEL=BAAI/bge-m3` to evaluate the larger multilingual candidate.
Embedding and PDF layout/OCR models may download on first use.

```powershell
# Build explicitly, or rebuild after changing knowledge in a running service:
.\.venv\Scripts\python.exe -c "from app.rag.retriever import KnowledgeRetriever; KnowledgeRetriever(build=False).build_index()"

# Run offline unit/integration tests without an LLM service:
.\.venv\Scripts\python.exe -m pytest -q
```

`build=False` loads/builds on the first search. Initialization reuses an index when
source hashes, model and chunk settings match. A running process retains its in-memory
index until explicit rebuild or restart. Identical files are indexed once.

Generated files live in the Git-ignored `app/storage/` directory:

```text
parsed/<checksum>.json + .md       # Docling exports
images/<checksum>/...             # extracted pictures / original image inputs
indexes/current.json              # active generation and pipeline settings
indexes/<generation>/
  faiss.index
  chunks.jsonl
  metadata.db                     # document / parent / child relationships
```

A generation is published after its files are saved. Old generations are retained;
automatic cleanup, index repair and multi-user permissions are outside this round.
Index files are local, trusted application data.

### Document processing

The ingestion-to-chunking path now runs:

```text
DoclingParser -> CrossPageMerger.merge(blocks) -> StructureRecovery.recover(blocks)
              -> ParentChunker -> ChildChunker -> FAISS + BM25
```

- Cross-page merging only considers adjacent pages in the same document and section.
  It joins unfinished sentences, reconciles repeated table headers, appends rows and
  joins blank-ID row continuations. Ordered lists retain numbering and do not join a
  restarted sequence. Explicit/repeated page furniture and boundary page numbers are
  removed. Continuation headings are mapped back to the existing section.
- Structure recovery uses numbering, source font/line measurements, bold text, indentation,
  known short topic headings and entity anchors. Unheaded topic groups require agreement
  between neighbouring paragraphs. Native heading paths remain authoritative.
- `BlockLayout` stores available layout signals. DOCX font sizes/indents come from source
  paragraphs; PDF cell heights/font names and page coordinates are used when available.
  Missing measurements are left unset. Inferred structure is marked `inferred` with a
  rule name/confidence; ambiguous unheaded content stays `unknown`. No LLM calls are made.
- `source_block_ids`, page ranges and `merge_reason` retain the provenance of merged
  evidence. Children inherit the original source IDs. Raw Docling JSON/Markdown archives
  remain unchanged. The index pipeline version was bumped so old indexes rebuild on load.

These are rule-based heuristics, not a guarantee that ambiguous page layouts can be
reconstructed. OCR accuracy and unusual continuation patterns need representative-file
acceptance testing rather than more speculative rules.

### Validation and next steps

`tests/test_api.py` and `tests/test_analysis.py` restore regression coverage for alert
listing/filtering/detail, health, deduplication, risk, analysis, HTTP errors and typed
analysis output. Tests use local LLM/embedding doubles instead of a removed production
`MockLLM` or remote services. The runtime explicitly requires Pydantic v2 and python-docx.

The v1.1 corpus adds 15 checked-in PDF, DOCX, XLSX, PPTX and PNG files with
checksums, sources and explicit expectations. Four inputs come from NIST/Docling;
eleven are generated boundary fixtures. See
[the corpus guide](tests/fixtures/rag_documents/README.md) for provenance, acceptance
checks and regeneration commands. This is structural regression coverage, not a
Recall/MRR/NDCG retrieval benchmark.

The four boundary fixes isolate source-image metadata from OCR items, require actual
list markers before joining cross-page lists, use contextual/layout evidence for
numbered headings, and align duplicate DOCX paragraphs by source occurrence rather
than text-key overwrite. Repeated body text with known non-margin coordinates is
retained. The index pipeline version is now 3, so affected indexes rebuild on load.

The parser requires Docling 2.145+ and pypdfium2 5.14+. Image inputs use full-page OCR.
PDFs with no native text anywhere use full-page OCR too; text-bearing and mixed PDFs
retain PDF-aware OCR. Set `RAG_OCR_ENABLED=false` to disable OCR, not PDF layout/table
processing. The GitHub Actions workflow runs normal regressions, publishes JUnit
results, and offers a manual full-model run; remote CI execution is separate from
local validation.

Local Python 3.13 validation: `pip check` passed; `python -m pytest -q` reported
**55 passed, 8 skipped**; `python -m pytest -q --rag-models` reported **63 passed**
with cached local Docling/OCR models. Model-enabled coverage includes real scanned
PDFs and all three image fixtures; skipped tests are not counted as passes.

Deferred: retrieval benchmarks, reranking, VLM/image vectors, neighbour expansion and
report-level citation evaluation. A single oversized table row stays intact in its
parent, while children remain token-bounded. Legacy binary Office files, Qdrant and
knowledge graphs are not introduced.

## Example Investigation Flow
输入：
AL-001

系统：
1. Load alert

2. Calculate risk

3. Retrieve security knowledge

4. Build investigation context

5. Generate analysis

输出：
Attack:
Brute Force

Evidence:
Multiple failed login attempts

Recommendation:
Block IP
Enable MFA
Investigate account
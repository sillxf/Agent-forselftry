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
against the repository. The default embedding is `BAAI/bge-m3`, using the existing
Dense + BM25 + RRF Hybrid retrieval. MiniLM is retained as a historical benchmark only.
Remove an old `RAG_EMBEDDING_MODEL=all-MiniLM-L6-v2` override from your environment
or change it to `BAAI/bge-m3`; then rebuild the index and restart the running service.
The dual-query translation experiment is not enabled in production.
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
Model changes create a new index generation; previous generations are retained.
New BGE indexes use its tokenizer with the configured 400-token child cap, not the
MiniLM-frozen 254-token chunks used in the A/B/C experiment; its scores are not
a production acceptance result.

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

A generation is published only after its files are saved and its query components
are successfully prepared. The facade switches its in-memory references after the
atomic pointer replacement. Pre-publication failures leave the old index active.
Old generations are retained;
automatic cleanup, index repair and multi-user permissions are outside this round.
Index files are local, trusted application data.

### Composable retrieval

Query-time logic is implemented by `DenseRetriever`, `SparseRetriever`, `RRFFusion`,
`ParentContextBuilder` and `RetrievalPipeline` under `app/rag/retrieval/`.
`KnowledgeRetriever` is the compatibility facade coordinating ingestion, indexing,
`SnapshotRepository` persistence and the query pipeline. Its search API is unchanged.
Components can be constructed independently and injected into the pipeline; no
Reranker, compression or new evaluation phase is enabled by this refactor.
See [component responsibilities and examples](docs/rag_retrieval_pipeline.md).

### Document processing

`IngestionPipeline` in `app/rag/ingestion/pipeline.py` can run document processing
independently and return documents, Parents and Children without vector encoding or
index persistence. It receives the existing parser and chunkers; the caller supplies
the tokenizer and effective token budget. `KnowledgeRetriever` delegates its document
processing to this pipeline; index persistence is delegated to `SnapshotRepository`.
See [standalone ingestion usage](docs/rag_retrieval_pipeline.md#独立文档处理第一步提取).

`IndexingPipeline` in `app/rag/indexing/pipeline.py` accepts that existing chunk result,
encodes Child `search_text` and returns an in-memory `IndexSnapshot`. Rebuild vectors
with a different embedding function or vector-store factory without parsing again.
The facade delegates persistence and publication to `SnapshotRepository`; index formats
remain unchanged.
See [chunk reuse and indexing examples](docs/rag_retrieval_pipeline.md#独立索引构建第二步提取).

`SnapshotRepository` in `app/rag/indexing/snapshot_repository.py` saves/loads generations
and publishes `current.json`. Build order is now: ingestion → indexing → save a fresh
generation → prepare query components → publish the pointer → activate in memory.
Existing generations load without migration; no automatic cleanup, recovery or
multi-process coordination is introduced. See [snapshot lifecycle](docs/rag_retrieval_pipeline.md#快照仓库与兼容-facade第三四步整理).

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

## RAG retrieval benchmark (candidate v0.3.1)

Nine frozen documents and 30 English/Chinese questions are evaluated with Dense,
BM25Plus and Hybrid RRF. Child retrieval and Parent context have separate metrics.

```powershell
python scripts/run_rag_benchmark.py --retriever all --top-k 5 --offline
# Only after real human review:
python scripts/run_rag_benchmark.py --retriever all --offline --require-reviewed
```

**All 30 labels still need human review.** AI source checks are not approval.
`--require-reviewed` rejects pending labels. These are development results, not a
certified acceptance benchmark or an Agent accuracy/refusal evaluation.

Phase 2 separates table-rule fact IDs, preserves equivalent evidence as OR
alternatives, tests the existing `result-qrels-v2` metric contract and repairs PDF
figure-label/heading/column mistakes using source layout. It does not change the
production embedding model, RRF, Top-K or add a reranker. A separate four-group
Chinese/English/multilingual/dual-query experiment keeps original queries frozen.

See [the Phase 2 report](docs/rag_benchmark_phase2_report.md),
[benchmark commands](tests/rag_benchmark/README.md),
[dataset audit](tests/rag_benchmark/dataset/phase2_audit.md),
[human worksheet](tests/rag_benchmark/dataset/review.md), and
[Agent evaluation design — not implemented](docs/agent_evaluation_design.md).

Historical v0.1/v0.2 experiment directories remain unchanged. Their differing
annotation/metric conventions are recorded in their own reports; do not interpret
old score-definition changes as retrieval improvements. The latest report records
actual test/CI results and explicitly distinguishes skipped PDF/OCR tests.


For a question-by-question comparison of reference answers, actual HTTP-route
retrieval and gold-blind LLM-generated answers, see the
[actual answer review](evaluation_results/baselines/2026-11-01_http_answer_review_candidate_v2/review.md).
This exploratory evaluation adds generation in its script; `/knowledge/search`
itself remains a retrieval-only endpoint. Prior named human approvals have been
withdrawn; development comparisons do not require manually approving each label.

The current development reference is documented in
[the retrieval reference](docs/rag_retrieval_reference.md): Parent Evidence
Recall@3 is 92% on 25 answerable questions. This is not generated-answer accuracy.

## Production / evaluation boundary

Production parsing, indexing and retrieval live in `app/rag/`. Dataset runners,
metrics, experiments and evaluation-only answer generation live in
[`evaluation/`](evaluation/README.md). The application never imports that package.
Existing scripts remain CLI entry points. Agent evaluation has its own reserved
`evaluation/agent/` package; its runner/judges/metrics are not implemented yet.

## Security Benchmark V1 — 100 candidate questions

The extended dataset is isolated in `tests/rag_benchmark/v1/`; the original
30 questions and historical results remain unchanged. It contains 21 frozen
sources, cross-language/indirect/confusable-technique cases and 10 unanswerable
questions. Every label and experimental translation remains pending review.

- [Usage, measured MiniLM results and A/B/C commands](docs/rag_benchmark_expansion.md)
- [Coverage audit](tests/rag_benchmark/dataset/benchmark_expansion_report.md)
- [100-question source review sheet](tests/rag_benchmark/v1/dataset/review.md)
- [Actual grouped multi-K results](evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm/hybrid/multik_report.md)

The completed A/B/C comparison is archived in
`evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/abc_report.md`.
BGE-M3 is now the default embedding. Frozen translated-query experiments do not
imply an online translation chain, Cross-Encoder or Agent refusal judge.

## Current milestone — 2026-11-02

The current RAG evaluation phase is complete for now: Benchmark V1 and the
MiniLM/BGE-M3 A/B/C comparison are archived, and `BAAI/bge-m3` is now the default
embedding with the existing Hybrid retrieval. The local production index was rebuilt;
Chinese-query API and Agent Top2 retrieval smoke checks passed. Regression tests:
123 passed, 10 skipped (PDF/OCR model tests requiring explicit opt-in).

Further work on the improvement plan is paused pending a new instruction. This is
a stopping milestone for this evaluation phase, not completion of all planned Agent
features; no Reranker, online translation chain or new refusal mechanism is enabled
by this milestone. Existing service processes need a restart to load the new defaults.


## Optional Question Multi-View — 2026-11-02

An experimental `multi_view` mode augments original Dense retrieval with a separate
index of offline-generated Chinese/English questions. View hits map back to original
Child/Parent evidence before context building; generated questions never become citations.
Hybrid remains the default. No automatic retry, router, Summary/Entity views or Reranker.

The Agent now has a `knowledge_search(query, retrieval_mode, top_k)` tool. Its mode enum
contains `multi_view` only when the active generation includes an auxiliary index.
`/knowledge/search` also accepts the optional mode; requesting a missing View index
returns 409 rather than silently running Hybrid. Old generations load unchanged.

The fixed 100-question pilot used the same BGE-M3 vectors, chunks, labels and retrieval
parameters. The original Hybrid ranking fingerprint is unchanged; neither arm had query errors.

| Parent metric | Hybrid | Question Multi-View |
| --- | ---: | ---: |
| All answerable Recall@5 | 94.44% | 84.44% |
| Chinese → English Recall@5 | 92.31% | 74.36% |
| All answerable Recall@10 | 97.78% | 97.78% |
| All answerable MRR@5 | 0.7448 | 0.6807 |

This implementation did **not** improve overall retrieval: one question gained Recall@5,
ten lost it. Auxiliary views are not published to the current production knowledge base.
The mode is available for explicit experiments, not recommended as the default or claimed
as a validated LLM routing improvement. No labels or human-review statuses were changed.

See [generation/build/replay commands](docs/rag_multiview.md) and
[the full comparison and per-question rank changes](evaluation_results/baselines/2026-11-02_security_v1_question_multiview/comparison.md).

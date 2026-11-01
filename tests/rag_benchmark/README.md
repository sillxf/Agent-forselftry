# Reproducible RAG retrieval benchmark

## Scope

This is a small evaluation module around the existing Retriever, not a new RAG
framework. It evaluates **retrieval only**. No LLM, judge, reranker, VLM, database
migration or embedding change is introduced.

- Nine fixed documents: real project knowledge, pinned ATT&CK/OWASP text, a NIST
  excerpt and three existing boundary fixtures. See `SOURCES.md` and `manifest.json`.
- Thirty explicitly **human-unreviewed candidate** questions. See `dataset/README.md`.
- Dense, BM25Plus and existing RRF hybrid rankings over one shared actual index.
- Separate Child ranks and unique-Parent ranks, with source evidence mapping.

## Run

From the repository root:

```powershell
python -m pip install -r requirements.txt
python scripts/run_rag_benchmark.py --retriever all --top-k 5
```

The first run may download the configured Sentence Transformers and Docling PDF/OCR
models. With models already cached:

```powershell
python scripts/run_rag_benchmark.py --retriever all --top-k 5 --offline
python scripts/run_rag_benchmark.py --retriever hybrid --top-k 5 --offline
```

Use `--require-reviewed` after actual human review; it intentionally fails for the
currently pending dataset. `--dataset`, `--model`, `--parent-tokens`, `--child-tokens`,
`--overlap-tokens`, `--dense-top-k`, `--bm25-top-k`, `--storage-dir` and `--output-dir`
allow explicit experiments. Do not change several major variables in one comparison.
No output directory is overwritten. Relative CLI paths are relative to the shell;
default paths resolve against the repository rather than the current directory.

Only `tests/rag_benchmark/documents/` is indexed. Dataset and source manifests are
validated against actual document hashes; the runner then validates every annotated
Block/quote/location against the built index **before** calculating any metric.
Changed/missing/additional documents and stale annotations are errors, not misses.

## Outputs

Each run creates an independent `evaluation_results/<timestamp>/` directory. With
`--retriever all`, each strategy has:

```text
config.json
retrieval_results.jsonl
metrics.json
failures.json
report.md
```

The run root also contains `comparison.json`, `comparison.md` and an exact
`source_snapshot.zip` of app/scripts Python code plus requirements (never `.env`,
credentials or model weights). This makes uncommitted-code experiments auditable:
commit, dirty flag, implementation hash and snapshot hash are explicit.
Dataset/corpus hashes, model weight/tokenizer hashes, cached model revision if
available, dependency versions, chunk parameters, effective model token limit,
BM25Plus parameters, RRF constant, candidate limits, index hash and setup time/size
are recorded. Tokenizer hashes exclude transient padding/truncation state changed
by `encode()`. `ranking_sha256` excludes timings and normalizes storage-local image
locations to document-hash/file suffixes. Raw results and raw chunk-file hashes still
retain their real paths; portable chunk fingerprints permit storage-independent
comparisons without claiming raw files are byte-identical. Index setup may load a reused generation; `setup_seconds` must not be
misreported as a fresh build duration. The snapshot alone is not an independent
package: pair it with the recorded dataset/corpus and compatible model/dependencies.

Latency is per-query retrieval time, excludes scoring/setup, and includes the first
query without special warmup. All-strategy execution is sequential, so cache effects
mean these timings are diagnostics, not a controlled throughput benchmark.
Raw unknown-query neighbours are preserved; the runner never replaces them with an
empty list just because the label says `answerable: false`.

## Exact ranking and metric conventions

1. `search_rankings()` exposes the existing pre-parent-dedup Child candidate ranking.
   The legacy `search()` response is unchanged. Dense/BM25 use their existing scoring;
   hybrid uses the unchanged RRF constant 60 and tie breaking. Candidate pool limits
   remain `max(configured_top_k, K*4)`.
2. Child Top K and unique-parent Top K are **independent ranking units**. Parent
   candidates may come from Child ranks beyond K, just as in the production search.
3. Evidence matches require document ID, source-Block intersection **and** a normalized
   verbatim quote in the actual Child or Parent content. Child `block_ids` currently
   describe whole source groups (tables may also span multiple rows), so intersection
   alone would falsely credit another slice/row. Quote matching closes that gap.
4. Keep unmatched and repeated result slots at their original ranks. Never remove
   misses before computing MRR or promote a rank-2 hit to rank 1. Duplicate evidence
   is credited only at first occurrence within the evaluated list.
5. Recall@K = unique positive evidence found in the first K result slots / all positive
   evidence labels. A result can cover multiple labels.
6. Precision@K = slots introducing at least one new positive evidence / **fixed K**,
   including when fewer than K results are returned. This novelty-aware convention
   intentionally penalizes duplicate evidence and must remain fixed across runs.
7. MRR@K = reciprocal of the first positive result rank, or zero if absent.
8. NDCG@K uses the maximum newly covered evidence grade at each result rank, gain
   `2^grade - 1`, discount `log2(rank + 1)`, and ideal graded **evidence** ordering.
   This explicitly defined novelty-aware evidence metric is not a claim of a fully
   judged chunk-level qrels benchmark; unknown/unjudged matches score zero.
9. Unanswerable questions have null ranking metrics and are excluded from macro
   averages. Their return/no-result counts are separate. No refusal accuracy is
   invented: a nearest neighbour is not an Agent decision or generated answer.
10. Parent context evidence coverage is reported separately. Context character count
    is only a size diagnostic; genuine context-noise/semantic precision is not yet
    annotated and is not fabricated from text length.

Reports aggregate by category, difficulty and source-document type. Retrieval errors
are retained as explicit failures, count as zero for answerable questions and cause
the CLI to exit nonzero. Source validation failures stop the run instead of producing
misleading scores. `failures.json` records missing/partial evidence, poor first rank,
incomplete parent coverage and exceptions with raw results and provenance.

## Tests and current baseline audit

```powershell
python -m pytest -q
python -m pytest -q --rag-models
```

New tests cover rank/duplicate semantics, graded NDCG, empty/short results, table-row
mapping, schema/corpus integrity, actual Retriever adaptation, unknown queries and
error recording, with deterministic local embedding doubles. They do not download
models in the normal test suite. Real embeddings are used in the separately run
baseline; test doubles are never presented as a real Dense benchmark.

At implementation start, local branch `main` and remote `main` both referenced
`e4a67efaef2850fdda7509d698a20455e7961086`. The existing default suite was rerun:
55 passed, 8 skipped; `pip check` passed. After implementation, the default suite
passed 69 tests with 8 model cases skipped; the full model-enabled suite passed all
77 tests. The saved candidate baseline uses real cached MiniLM and Docling models.
One full rerun emitted an intermittent native Docling `access violation` diagnostic
while still completing with exit code 0 and 77 passed; another full run was clean.
The saved `analysis.md` and test logs explicitly record this dependency risk. GitHub Actions API verification returned
HTTP 403 (rate limit), so remote CI success remains **unverified**.

The handoff's concern about a missing `test-results` directory is not itself a
confirmed bug: the installed pytest JUnit plugin calls `os.makedirs(..., exist_ok=True)`
before writing XML. The workflow has not been modified merely to add a redundant
workaround. New focused tests are collected by its existing pytest command.

## Acceptance boundary

The engineering runner and provisional baseline can be delivered now. The planning
requirement of **30 human-reviewed questions** is NOT fulfilled by AI source checks.
Until a human signs off the labels, all reports remain candidate/development results.
The included data is small, not a holdout sample and cannot establish broad accuracy.

Next steps should be based on the failure files: first review labels, language
mismatches and source metadata; only then consider reranking or other algorithmic
changes, one variable at a time. No retrieval tuning is done by this implementation.

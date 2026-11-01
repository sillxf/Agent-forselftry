# Candidate baseline analysis — 2026-11-01

## Status

These are measured results, **not human-certified acceptance scores**. All 30
candidate annotations still require human relevance review. Twenty-five answerable
questions contribute to ranking averages; five unknown questions are separate.
This is a small development dataset, not a statistically representative holdout set.

## Observations supported by this run

- Child evidence Recall@5: Dense 0.84, BM25 0.84, Hybrid 0.88.
- Child MRR@5: Dense 0.6913, BM25 0.6833, Hybrid 0.8133.
- Hybrid parent evidence coverage@5 is 0.92, compared with child coverage 0.88.
  These are different ranking units, not a claim that adding context always helps.
- Under Hybrid, `rag_004` (OWASP test identifier) misses the exact evidence at the
  Child level but finds it in restored Parent context. Inspect the ID-table child,
  repeated section prefixes and actual ranks before changing any retrieval logic.
- `rag_011` and `rag_014` miss both Child and Parent evidence in all three strategies.
  Both use Chinese questions over English project guidance. Language mismatch is a
  plausible explanation, not a proven root cause. Check the labels and queries
  before proposing a controlled multilingual-embedding experiment.
- `rag_002`, `rag_003` and `rag_016` have relevant Hybrid evidence in Top 5 but not
  at rank 1. This separates ranking failures from absent evidence.
- All five unanswerable questions return Hybrid neighbours. This is expected from
  nearest-neighbour retrieval without an abstention mechanism and is **not** a
  measured answer hallucination or correct-refusal rate. Their actual results are
  retained instead of being replaced with empty lists from the answerability labels.
- Parent context size is measured in characters only. No semantic context-noise
  score or LLM answer quality is claimed.

## Independent reproducibility check

A second process rebuilt the index into a separate, initially absent storage
folder, then repeated all 30 questions for Dense/BM25/Hybrid (90 query runs).
`reproducibility_check.json` and `rebuild_configs/` record this verification.

- Model weight and canonical tokenizer fingerprints matched.
- FAISS vector-index bytes matched exactly across independent generations.
- Portable chunk fingerprints matched.
- All Child/Parent rankings, scores and quality metrics matched, after normalizing
  only storage-local image-path prefixes. Timings were intentionally excluded.
- Raw `chunks.jsonl` hashes differ because extracted-image absolute paths point at
  different storage folders; this is recorded, not called byte-identical output.
- The check validates this same-machine environment. It does not guarantee identical
  floating-point scores across hardware or different dependency/model versions.

## Validation and dependency diagnostics

Default tests: 69 passed, 8 explicitly skipped model cases. Full model-enabled tests:
77 passed. `pip check` and Python compile checks passed. Test logs/XML are retained
under `test-results/` for this baseline.

One full-suite rerun emitted a Windows `access violation` diagnostic from the
`docling_parse` PDF producer thread, but the same process completed with exit code 0
and 77 passed. Another full run completed without that diagnostic. This intermittent
native dependency issue was also seen during earlier PDF validation; it is recorded
as an environment/dependency risk, not suppressed or reported as a clean diagnostic
run. No unrelated PDF-backend replacement was bundled into this benchmark change.

GitHub Actions verification was rate-limited (HTTP 403). Remote CI is unverified.
The pytest JUnit plugin creates output directories itself; no redundant workflow
change was made based solely on the handoff's directory-creation concern.

## Next steps, not automatically implemented

1. Complete human review, including alternate relevant sources and unknown questions.
2. Freeze reviewed labels and an independent holdout sample before tuning.
3. Inspect the recorded language and table-ID ranking failures.
4. Change one variable per experiment; do not infer that reranking or a new model
   will help merely because it is available.

No Reranker, LLM judge, VLM, neighbor expansion, Graph RAG or index migration was added.

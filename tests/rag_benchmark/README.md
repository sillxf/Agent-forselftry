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
`source_snapshot.zip` of app/evaluation/scripts Python code plus requirements (never `.env`,
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
4. An evidence entry is one required fact. Its `alternatives` are equivalent source
   locations: matching any one supports that fact once. Distinct required facts are
   still separate entries; translations do not inflate the Recall denominator.
5. Keep unmatched slots and distinct overlapping children at their original ranks.
   Recall@K counts unique positive facts found / all positive facts. Repeated coverage
   of one fact does not increase Recall. One result may cover several facts.
6. Precision@K counts relevant result slots / **fixed K**, even if fewer than K results
   exist. Each distinct indexed Child/Parent is one result; two different units can
   both be relevant to the same fact. MRR uses the first relevant result rank.
7. NDCG@K now uses **result-level qrels**, contract `result-qrels-v2`. Each indexed
   result's grade is the maximum grade of the facts it supports; gain is `2^grade-1`,
   discount `log2(rank+1)`. IDCG uses the sorted grades of ALL indexed units of that
   same type, independently of the query's returned candidate pool. It is not derived
   from evidence counts or just Top K. Qrels are stored per question for inspection.
8. This corrects the v0.1 mismatch between result-based DCG and evidence-based IDCG,
   which penalized one result containing several facts. Precision also no longer
   silently implements a novelty-only measure. **Old and new Precision/NDCG values
   are not comparable as algorithm improvements.** Original ranks are preserved;
   the audit verifies query/rank/score identity against the earlier run.
9. Qrels are deterministic mappings from source annotations, not independently
   human-judged chunk labels. Unknown/unjudged matches score zero. These remain
   provisional until relevance review; short quotes can still have semantic limits.
   Only body text is scored: an answer visible solely in `section_path` is a separate
   metadata diagnostic, not silently counted for only the questions it would help.
10. Unanswerable questions have null ranking metrics and are excluded from macro
    averages. Their actual return/no-result counts are separate; no refusal accuracy
    is invented. Parent coverage is separate; character length is not context noise.

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

The original implementation's local base commit was `e4a67ef`, followed by benchmark
commit `1cd53a2`. Original validation passed 69 default tests (8 model skips) and all
77 model-enabled tests. One rerun logged an intermittent native Docling access violation
while exiting 0; another full run was clean. Historical artifacts remain immutable.

During the source audit, the GitHub API was successfully accessed directly (the proxy
was rate-limited). It confirmed commit `1cd53a2cb596275a45c999eda6dd6079752d48a2`
passed Actions run `41267810301`: install, pip check, default pytest and upload were
successful. The optional full-model step was **skipped**. This does not verify CI for
uncommitted audit edits. The fetched run/job records are saved with the new report.

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

## Source audit and human acceptance packet

The v0.2 source-audited candidate keeps all original queries/answers and corpus bytes.
Eight annotations were corrected for sufficient anchors and equivalent locations;
`dataset/annotation_changes.json` preserves before/after labels. `dataset/audit_notes.json`
records all 30 AI source assessments and remaining human decisions. No approval is
inferred from this automation. The worksheet is `dataset/review.md`.

```powershell
python scripts/run_rag_benchmark.py --retriever all --top-k 5 --offline
# Audit a newly generated all-strategy run, and regenerate the human review sheet:
python scripts/audit_rag_benchmark.py --baseline evaluation_results/<run-directory>
```

The audit validates source anchors and index reachability, diagnoses candidate ranks
and token overlap, and compares raw queries/ranks/scores against the v0.1 baseline.
Two faithful English translations are run **only as diagnostics**, never substituted
for Chinese dataset questions or included in benchmark means. They support a language/
expression mismatch hypothesis but do not prove a specific model replacement is needed.

`--require-reviewed` intentionally still fails for all 30 pending labels. A human
must approve labels, grades, alternative sources and metric/body-evidence scope before
calling a subsequent frozen run an acceptance baseline. Source metadata discrepancies
are recorded rather than blessed because the parser and labels agree with each other.

Historical v0.2 source-audit validation: normal suite **70 passed, 8 skipped**, full model
suite **78 passed**. Latest logs have no native access-violation diagnostic; earlier
intermittent dependency behaviour remains a recorded risk, not a proven fix.
The saved `2026-11-01_source_audit_v2/` report includes `source_audit.md`,
`score_reconciliation.json`, `ci_status.json`, frozen annotations, independent
rebuild records, test logs and a formal-acceptance checklist with human gates open.


## Phase 2: fact identity, PDF structure and cross-language experiments

Current annotations: **v0.3.1-structure-corrected-candidate**, still 30 human reviews
pending. Rule rows R002/R003/R004 have distinct IDs; NIST source paths were refreshed
after generic layout/container fixes. Queries, answers, evidence semantics, grades,
corpus bytes and the `result-qrels-v2` metric contract are unchanged.
Changes are recorded in `dataset/phase2_annotation_changes.json` and
`dataset/phase2_structure_location_changes.json`; see `dataset/phase2_audit.md`.

```powershell
python scripts/run_rag_benchmark.py --retriever all --top-k 5 --offline `
  --storage-dir app/storage/benchmark-phase2 `
  --output-dir evaluation_results/phase2-candidate
python scripts/analyze_rag_benchmark.py --baseline evaluation_results/phase2-candidate `
  --storage-dir app/storage/benchmark-phase2
python scripts/run_crosslingual_experiment.py --baseline evaluation_results/phase2-candidate `
  --storage-dir app/storage/benchmark-phase2 `
  --output-dir evaluation_results/phase2-crosslingual --offline
```

Cross-language groups A/B/C/D retain the original Chinese dataset queries. Fixed
literal translations live in `experiments/crosslingual_queries.json`, not the
main dataset. Group C uses an isolated multilingual FAISS index with **identical
frozen chunk texts/IDs**, not multilingual-tokenizer re-chunking; model-specific
truncation counts and build cost are recorded. Group D uses two query routes,
so its extra compute/candidates are explicit. Default models/query policies do
not change. The multilingual model must be downloaded once before offline runs.

New runs archive replayable dataset/corpus snapshots alongside source code,
metrics, Child/Parent diagnostics and raw ranks. Failure analysis traces correct
facts to indexed IDs and the original candidate pool, with cause hypotheses
explicitly separated from evidence. Unknown cases retain misleading-neighbour
risks but do not pretend to measure Agent hallucination, knowledge-gap detection
or refusal. Agent evaluation remains a separate design task.

The earlier `audit_rag_benchmark.py` is a **historical v0.1/v0.2 reconciliation**;
it asserts unchanged rankings, so do not use it to compare the new parser run.
Use `analyze_rag_benchmark.py` for Phase 2. Never overwrite historical baselines.


Phase 2 delivery report: `docs/rag_benchmark_phase2_report.md` (repository root).
Current regular validation is 81 passed / 10 intentional model skips. The full
model run has 91 passed assertions and exit 0 **but printed a Windows native
access-violation diagnostic**; an isolated nine-test PDF rerun is clean. The issue
is not claimed fixed. All logs and the still-open human acceptance gate are saved.


## 实际答案对照（检索 + 评测专用生成）

原来的 `dataset/review.md` 只用于审核问题、参考答案及来源，不是实际回答记录。
要逐题比较真实输出，可以运行：

```powershell
.\.venv\Scripts\python.exe scripts/run_rag_answer_review.py --offline-models --generate --top-k 3 `
  --output-dir evaluation_results/new-http-answer-review
```

- 显式将本进程知识库设为 9 份固定测试文档，不修改默认 API 的三个 Markdown 或 `.env`。
- 通过 FastAPI TestClient 调用真实 `/knowledge/search` 路由，不替换检索器、Embedding 或返回结果；这不是对已经运行的网络服务实例发请求。
- Top-K 默认 3，与接口默认值一致。当前可复用 `app/storage/benchmark-phase2` 的真实索引，也可用 `--storage-dir` 指定新索引目录。
- `--generate` 使用现有 LLM 配置，将实际返回的完整片段生成答案。这是评测脚本增加的生成步骤，不是 `/knowledge/search` 已有的功能。
- 生成提示只含问题及检索片段，不含参考答案、相关性标注、可回答标签或审核意见。
- `--offline-models` 仅限制 Embedding/解析模型；生成仍访问 `.env` 配置的 LLM 服务。每题生成默认超时 120 秒，不自动重试。
- 输出 `review.html`（左右对照）、`review.md`、`results.jsonl`（原始 HTTP JSON、生成提示及返回）、`run.json`、标注快照和源码快照。
- 证据覆盖不等于答案正确。此前署名人工审核已撤销；候选对比无需逐题审批，不能把旧的通过状态沿用为当前结论。
- 这是探索性运行，不使用 `--require-reviewed`，不能取代尚未放行的正式基线。输出目录不得覆盖已有结果。

2026-11-01 的实际输出见：
[`review.html`](../../evaluation_results/baselines/2026-11-01_http_answer_review_candidate_v2/review.html) ·
[`review.md`](../../evaluation_results/baselines/2026-11-01_http_answer_review_candidate_v2/review.md)。

本次运行已作为后续迭代的开发参考：宏平均 Parent Evidence Recall@3 为 92%，
完整证据覆盖 23/25，按题累计事实召回为 37/43。不是最终答案正确率。
此前署名人工审核已撤销，当前数据集不保留其批准状态；历史原始快照仅用于追溯。
具体口径、已知失败与后续比较方法见
[开发参考基准](../../docs/rag_retrieval_reference.md)。

## 代码位置与依赖边界

评测实现已从 `app/rag/evaluation/` 移到顶层 `evaluation/rag/`；
`retrieval_metrics.py` 改名为 `metrics.py`，指标定义不变。
`run_rag_benchmark.py`、`run_rag_answer_review.py` 等原命令保留为薄入口。
源码归档包含新 `evaluation/` 包，旧封存结果与输入数据没有改写。
完整分工见 [评测目录说明](../../evaluation/README.md)。

## 100 题扩展版（独立输入，不覆盖原 30 题）

新数据在 `v1/dataset/questions.jsonl`，主候选版本为 r2；分布、来源、逐题 Ground Truth 和状态均可审查。
新的多 K 评测使用同一个深度 10 排名，输出 Recall@1/3/5/10、Precision/MRR/NDCG@5 和题型/语言分组。
不可答题不进入普通 Recall/MRR，邻近上下文返回单列，不能冒充 Agent 拒答测试。

[完整指南与实际 A 结果](../../docs/rag_benchmark_expansion.md) ·
[覆盖报告](dataset/benchmark_expansion_report.md) ·
[新题逐题审核](v1/dataset/review.md)。

BGE-M3 / 双路 Query + 英文 BM25 + RRF 的代码与命令已准备；本地无 BGE 缓存，尚无 B/C 实测分数。
生产 RAG 和原来 30 题的开发参考保持不变。

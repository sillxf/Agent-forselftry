# bm25 retrieval baseline

Status: **provisional**; 30 labels pending human review.
Dataset: `rag-benchmark-v0.1-candidate` / `16e23a4015636b2de67c6419c3cb589369e0112b8dedfe5904c95840d1294729`.
Code: `e4a67efaef2850fdda7509d698a20455e7961086`; dirty=True; source SHA-256 `41692b4db54b6c5725f40ba852e4e1d7f3828807504f49dc229bf882efdf40db`.

Questions: 30; answerable: 25; unanswerable: 5.

| Ranking unit (K=5) | Evidence Recall | Novel-hit Precision | MRR | Evidence NDCG |
| --- | ---: | ---: | ---: | ---: |
| child | 0.8400 | 0.1920 | 0.6833 | 0.6638 |
| parent | 0.8400 | 0.1760 | 0.6900 | 0.6413 |

Child K and unique-parent K are different ranking units; do not combine them.
Unmatched and duplicate slots keep their original ranks. Recall counts unique positive evidence;
Precision counts ranks introducing new positive evidence / fixed K. NDCG uses maximum new grade
per rank, gain 2^grade-1 and evidence-level IDCG. A result may cover several evidence labels.
Grades 1–3 count as positive. These novelty-aware conventions must remain fixed across experiments.

## Categories

| Category | Questions | Child Recall | Child MRR | Parent Recall |
| --- | ---: | ---: | ---: | ---: |
| context | 5 | 1.0000 | 0.8000 | 1.0000 |
| exact_identifier | 5 | 0.8000 | 0.4667 | 0.8000 |
| response | 5 | 0.6000 | 0.6000 | 0.6000 |
| semantic | 5 | 1.0000 | 0.7500 | 1.0000 |
| tables_steps | 5 | 0.8000 | 0.8000 | 0.8000 |
| unanswerable | 5 | N/A | N/A | N/A |

## Engineering diagnostics

Errors: 0; no-result rate: 0.0333.
Retrieval latency ms (mean/P50/P95): 2.80 / 2.50 / 4.94.
Latency excludes model/index setup and evidence scoring. The first query is not warmed separately.
Mean parent context length: 8121.5 characters.
This is a size diagnostic, not a validated context-noise/precision metric.
Unanswerable cases are excluded from ranking averages; no refusal rate is inferred.

## Failures

- `rag_002`: first_result_not_relevant — What technique is assigned the ATT&CK identifier T1110?
- `rag_003`: first_result_not_relevant — Which ATT&CK technique name corresponds to T1078?
- `rag_004`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — Which OWASP WSTG test identifier covers SQL injection?
- `rag_005`: first_result_not_relevant — 检测规则 R002 的严重程度和响应动作是什么？
- `rag_007`: first_result_not_relevant — Can password guessing be performed without contacting a live authentication service?
- `rag_009`: first_result_not_relevant — How can a tester infer database information when no data is returned directly?
- `rag_011`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 暴力破解告警的本地响应清单建议采取哪些措施？
- `rag_014`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 本地 SQL 注入知识库列出了哪些预防措施？
- `rag_018`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — What are the three numbered actions in the response checklist, in order?
- `rag_022`: first_result_not_relevant — Why does NIST Rev. 3 emphasize cybersecurity risk management instead of maintaining every detailed response procedure?
- `rag_024`: first_result_not_relevant — What cross-account authentication indicators and matching response actions are listed in the brute-force guide?

## Scope and limitations

All source evidence and quotes were checked against the actual index before evaluation.
Pending labels are AI-prepared candidates, not human-certified ground truth. Review alternative
valid sources, grades and unanswerable rationales before treating these scores as acceptance results.
This small development set is not a holdout benchmark and does not establish general accuracy.
No LLM answer generation, judge, reranker, embedding migration or automatic tuning was performed.
Read `retrieval_results.jsonl` and `failures.json` for full ranks, scores, quotes and provenance.

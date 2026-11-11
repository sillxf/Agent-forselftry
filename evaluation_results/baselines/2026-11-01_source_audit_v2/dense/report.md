# dense retrieval baseline

Status: **provisional**; 30 labels pending human review.
Dataset: `rag-benchmark-v0.2-source-audited-candidate` / `070cda0b190aa3b41f2ad058ecf9a28f1190e6d11c693fcb5f776646cbb38cbf`.
Code: `1cd53a2cb596275a45c999eda6dd6079752d48a2`; dirty=True; source SHA-256 `2fcf44975ad79e4a3e9dcf020d7096863307c12a4a9ae0d4f28d89b6e50d9eb4`.

Questions: 30; answerable: 25; unanswerable: 5.

| Ranking unit (K=5) | Evidence Recall | Result Precision | MRR | Result NDCG |
| --- | ---: | ---: | ---: | ---: |
| child | 0.8400 | 0.2240 | 0.6913 | 0.7296 |
| parent | 0.9200 | 0.1920 | 0.7933 | 0.8274 |

Child K and unique-parent K are different ranking units; do not combine them.
Metric contract: `result-qrels-v2`. Recall covers unique required facts; alternatives are OR locations.
Precision is relevant result slots / fixed K. Multiple distinct results supporting one fact remain relevant.
DCG uses max fact grade per result, gain 2^grade-1 and log2(rank+1) discount.
IDCG uses the sorted grades of ALL indexed units of the same type, not the number of facts.
Qrels are deterministically derived from body quotes and source IDs, not independently human-judged chunks.
Misses keep their rank. Metadata-only answers are not credited as body evidence.
Old v0.1 novelty/evidence metrics used a different definition and are not directly comparable.
No search, embedding, chunking or RRF change is implied by an evaluation score change.

## Categories

| Category | Questions | Child Recall | Child MRR | Parent Recall |
| --- | ---: | ---: | ---: | ---: |
| context | 5 | 1.0000 | 0.9000 | 1.0000 |
| exact_identifier | 5 | 0.8000 | 0.4067 | 1.0000 |
| response | 5 | 0.6000 | 0.6000 | 0.6000 |
| semantic | 5 | 1.0000 | 0.9000 | 1.0000 |
| tables_steps | 5 | 0.8000 | 0.6500 | 1.0000 |
| unanswerable | 5 | N/A | N/A | N/A |

## Engineering diagnostics

Errors: 0; no-result rate: 0.0000.
Retrieval latency ms (mean/P50/P95): 11.56 / 11.18 / 14.19.
Latency excludes model/index setup and evidence scoring. The first query is not warmed separately.
Mean parent context length: 6811.7 characters.
This is a size diagnostic, not a validated context-noise/precision metric.
Unanswerable cases are excluded from ranking averages; no refusal rate is inferred.

## Failures

- `rag_001`: first_result_not_relevant — T1059.001 refers to which Windows scripting environment?
- `rag_002`: first_result_not_relevant — What technique is assigned the ATT&CK identifier T1110?
- `rag_003`: first_result_not_relevant — Which ATT&CK technique name corresponds to T1078?
- `rag_004`: no_relevant_child, first_result_not_relevant — Which OWASP WSTG test identifier covers SQL injection?
- `rag_009`: first_result_not_relevant — How can a tester infer database information when no data is returned directly?
- `rag_011`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 暴力破解告警的本地响应清单建议采取哪些措施？
- `rag_014`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 本地 SQL 注入知识库列出了哪些预防措施？
- `rag_016`: first_result_not_relevant — For detection rule R004, what severity and response are specified?
- `rag_020`: no_relevant_child, first_result_not_relevant — When enumerating SQL-injection inputs, should hidden POST fields, HTTP headers and cookies be included?
- `rag_024`: first_result_not_relevant — What cross-account authentication indicators and matching response actions are listed in the brute-force guide?

## Scope and limitations

All source evidence and quotes were checked against the actual index before evaluation.
Pending labels are AI-prepared candidates, not human-certified ground truth. Review alternative
valid sources, grades and unanswerable rationales before treating these scores as acceptance results.
This small development set is not a holdout benchmark and does not establish general accuracy.
No LLM answer generation, judge, reranker, embedding migration or automatic tuning was performed.
Read `retrieval_results.jsonl` and `failures.json` for full ranks, scores, quotes and provenance.

# hybrid retrieval baseline

Status: **provisional**; 30 labels pending human review.
Dataset: `rag-benchmark-v0.3.1-structure-corrected-candidate` / `04cadb9bab07b00e64a2e2011274493497dc9e64d4e63ef945a5e60128dee3b7`.
Code: `7dbd41eec127f13fa442181e9a5f18eb419b4503`; dirty=True; source SHA-256 `07e73e2260450350d0ea5e1089177016d313f53e86fb10e4632c187ac7b3cb14`.

Questions: 30; answerable: 25; unanswerable: 5.

| Ranking unit (K=5) | Evidence Recall | Result Precision | MRR | Result NDCG |
| --- | ---: | ---: | ---: | ---: |
| child | 0.8800 | 0.2240 | 0.8133 | 0.8305 |
| parent | 0.9200 | 0.1920 | 0.8600 | 0.8757 |

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
| context | 5 | 1.0000 | 1.0000 | 1.0000 |
| exact_identifier | 5 | 0.8000 | 0.5667 | 1.0000 |
| response | 5 | 0.6000 | 0.6000 | 0.6000 |
| semantic | 5 | 1.0000 | 1.0000 | 1.0000 |
| tables_steps | 5 | 1.0000 | 0.9000 | 1.0000 |
| unanswerable | 5 | N/A | N/A | N/A |

## Engineering diagnostics

Errors: 0; no-result rate: 0.0000.
Retrieval latency ms (mean/P50/P95): 22.26 / 21.95 / 25.39.
Latency excludes model/index setup and evidence scoring. The first query is not warmed separately.
Mean parent context length: 7374.1 characters.
This is a size diagnostic, not a validated context-noise/precision metric.
Unanswerable cases are excluded from ranking averages; no refusal rate is inferred.

## Failures

- `rag_002`: first_result_not_relevant — What technique is assigned the ATT&CK identifier T1110?
- `rag_003`: first_result_not_relevant — Which ATT&CK technique name corresponds to T1078?
- `rag_004`: no_relevant_child, first_result_not_relevant — Which OWASP WSTG test identifier covers SQL injection?
- `rag_011`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 暴力破解告警的本地响应清单建议采取哪些措施？
- `rag_014`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 本地 SQL 注入知识库列出了哪些预防措施？
- `rag_016`: first_result_not_relevant — For detection rule R004, what severity and response are specified?

## Scope and limitations

All source evidence and quotes were checked against the actual index before evaluation.
Pending labels are AI-prepared candidates, not human-certified ground truth. Review alternative
valid sources, grades and unanswerable rationales before treating these scores as acceptance results.
This small development set is not a holdout benchmark and does not establish general accuracy.
No LLM answer generation, judge, reranker, embedding migration or automatic tuning was performed.
Read `retrieval_results.jsonl` and `failures.json` for full ranks, scores, quotes and provenance.

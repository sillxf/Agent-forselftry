# Candidate retrieval comparison

Annotation status: **provisional**. Do not treat pending labels as human-reviewed acceptance.
All strategies share the same corpus, index, embedding and chunking configuration.

K is identical, but Child and Parent are separate result universes.

## Child Retrieval Metrics

| Strategy | Recall@K | Precision@K | MRR@K | NDCG@K |
| --- | ---: | ---: | ---: | ---: |
| dense | 0.4167 | 0.0978 | 0.3861 | 0.3914 |
| bm25 | 0.4389 | 0.0978 | 0.3509 | 0.3640 |
| hybrid | 0.4611 | 0.1067 | 0.4217 | 0.4278 |

## Parent Retrieval Metrics

| Strategy | Recall@K | Precision@K | MRR@K | NDCG@K |
| --- | ---: | ---: | ---: | ---: |
| dense | 0.4917 | 0.1022 | 0.4343 | 0.4488 |
| bm25 | 0.4556 | 0.0933 | 0.3633 | 0.3878 |
| hybrid | 0.5028 | 0.1044 | 0.4593 | 0.4697 |


K=5. Recall is unique evidence coverage within K child or K unique-parent ranks.
Metric definitions changed from candidate v0.1. Do not interpret score differences as retrieval improvements.
Precision/NDCG use derived result-level qrels (contract result-qrels-v2); Recall covers unique facts. Unknown cases are excluded.
Only rank/metric comparisons are meaningful here; sequential strategy order affects cache/latency measurements.
The exact implementation is archived in source_snapshot.zip; config files record its hash.

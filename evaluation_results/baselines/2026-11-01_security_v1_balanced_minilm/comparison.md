# Candidate retrieval comparison

Annotation status: **provisional**. Do not treat pending labels as human-reviewed acceptance.
All strategies share the same corpus, index, embedding and chunking configuration.

K is identical, but Child and Parent are separate result universes.

## Child Retrieval Metrics

| Strategy | Recall@K | Precision@K | MRR@K | NDCG@K |
| --- | ---: | ---: | ---: | ---: |
| dense | 0.4833 | 0.1156 | 0.4454 | 0.4516 |
| bm25 | 0.5167 | 0.1178 | 0.4306 | 0.4433 |
| hybrid | 0.5278 | 0.1244 | 0.4754 | 0.4848 |

## Parent Retrieval Metrics

| Strategy | Recall@K | Precision@K | MRR@K | NDCG@K |
| --- | ---: | ---: | ---: | ---: |
| dense | 0.5583 | 0.1200 | 0.4954 | 0.5114 |
| bm25 | 0.5333 | 0.1133 | 0.4519 | 0.4738 |
| hybrid | 0.5694 | 0.1222 | 0.5204 | 0.5323 |


K=5. Recall is unique evidence coverage within K child or K unique-parent ranks.
Metric definitions changed from candidate v0.1. Do not interpret score differences as retrieval improvements.
Precision/NDCG use derived result-level qrels (contract result-qrels-v2); Recall covers unique facts. Unknown cases are excluded.
Only rank/metric comparisons are meaningful here; sequential strategy order affects cache/latency measurements.
The exact implementation is archived in source_snapshot.zip; config files record its hash.

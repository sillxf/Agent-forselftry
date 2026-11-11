# Candidate retrieval comparison

Annotation status: **provisional**. Do not treat pending labels as human-reviewed acceptance.
All strategies share the same corpus, index, embedding and chunking configuration.

| Strategy | Child Recall@K | Child Precision@K | Child MRR@K | Child NDCG@K | Parent Recall@K |
| --- | ---: | ---: | ---: | ---: | ---: |
| dense | 0.8400 | 0.2240 | 0.6913 | 0.7296 | 0.9200 |
| bm25 | 0.8400 | 0.2080 | 0.6833 | 0.7012 | 0.8400 |
| hybrid | 0.8800 | 0.2320 | 0.8133 | 0.8305 | 0.9200 |

K=5. Recall is unique evidence coverage within K child or K unique-parent ranks.
Metric definitions changed from candidate v0.1. Do not interpret score differences as retrieval improvements.
Precision/NDCG use derived result-level qrels (contract result-qrels-v2); Recall covers unique facts. Unknown cases are excluded.
Only rank/metric comparisons are meaningful here; sequential strategy order affects cache/latency measurements.
The exact implementation is archived in source_snapshot.zip; config files record its hash.

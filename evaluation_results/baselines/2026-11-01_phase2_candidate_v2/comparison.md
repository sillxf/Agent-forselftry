# Candidate retrieval comparison

Annotation status: **provisional**. Do not treat pending labels as human-reviewed acceptance.
All strategies share the same corpus, index, embedding and chunking configuration.

K is identical, but Child and Parent are separate result universes.

## Child Retrieval Metrics

| Strategy | Recall@K | Precision@K | MRR@K | NDCG@K |
| --- | ---: | ---: | ---: | ---: |
| dense | 0.8400 | 0.2160 | 0.6733 | 0.7166 |
| bm25 | 0.8800 | 0.2080 | 0.6913 | 0.7142 |
| hybrid | 0.8800 | 0.2240 | 0.8133 | 0.8305 |

## Parent Retrieval Metrics

| Strategy | Recall@K | Precision@K | MRR@K | NDCG@K |
| --- | ---: | ---: | ---: | ---: |
| dense | 0.9200 | 0.1920 | 0.7733 | 0.8127 |
| bm25 | 0.8800 | 0.1840 | 0.6980 | 0.7466 |
| hybrid | 0.9200 | 0.1920 | 0.8600 | 0.8757 |


K=5. Recall is unique evidence coverage within K child or K unique-parent ranks.
Metric definitions changed from candidate v0.1. Do not interpret score differences as retrieval improvements.
Precision/NDCG use derived result-level qrels (contract result-qrels-v2); Recall covers unique facts. Unknown cases are excluded.
Only rank/metric comparisons are meaningful here; sequential strategy order affects cache/latency measurements.
The exact implementation is archived in source_snapshot.zip; config files record its hash.

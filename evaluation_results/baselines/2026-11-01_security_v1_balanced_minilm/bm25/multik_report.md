# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.3333 | 0.4933 | 0.5167 | 0.5278 | 0.1178 | 0.4306 | 0.4433 |
| parent | 0.3648 | 0.5267 | 0.5333 | 0.5444 | 0.1133 | 0.4519 | 0.4738 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.7333 | 0.9333 | 0.9333 | 0.9333 | 0.8222 |
| question_type | mixed_terms | 15 | 0.6667 | 0.9333 | 0.9333 | 0.9333 | 0.8000 |
| question_type | multi_document | 5 | 0.1667 | 0.4000 | 0.4000 | 0.4000 | 0.4000 |
| question_type | paraphrase | 15 | 0.2667 | 0.6267 | 0.6667 | 0.7333 | 0.4556 |
| question_type | technique_confusion | 15 | 0.4667 | 0.5333 | 0.5333 | 0.5333 | 0.5000 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| language_pair | en->en | 35 | 0.6524 | 0.9257 | 0.9429 | 0.9714 | 0.8095 |
| language_pair | en->mixed | 1 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 0.6667 | 0.9333 | 0.9333 | 0.9333 | 0.8000 |
| language_pair | zh->en | 39 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.5000 | 0.8750 | 0.8750 | 0.8750 | 0.6875 |
| difficulty | hard | 51 | 0.3862 | 0.5463 | 0.5610 | 0.5610 | 0.4837 |
| difficulty | medium | 41 | 0.3171 | 0.4390 | 0.4390 | 0.4634 | 0.3740 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

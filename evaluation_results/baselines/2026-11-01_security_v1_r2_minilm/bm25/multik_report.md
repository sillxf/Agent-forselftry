# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.2685 | 0.4156 | 0.4389 | 0.4611 | 0.0978 | 0.3509 | 0.3640 |
| parent | 0.2889 | 0.4378 | 0.4556 | 0.4778 | 0.0933 | 0.3633 | 0.3878 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.7333 | 0.9333 | 0.9333 | 0.9333 | 0.8222 |
| question_type | mixed_terms | 15 | 0.6667 | 0.9333 | 0.9333 | 0.9333 | 0.8000 |
| question_type | multi_document | 5 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| question_type | paraphrase | 15 | 0.3333 | 0.7600 | 0.8667 | 1.0000 | 0.5578 |
| question_type | technique_confusion | 15 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| language_pair | en->en | 29 | 0.5517 | 0.8414 | 0.8966 | 0.9655 | 0.7023 |
| language_pair | en->mixed | 1 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.3333 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 0.6667 | 0.9333 | 0.9333 | 0.9333 | 0.8000 |
| language_pair | zh->en | 45 | 0.0000 | 0.0000 | 0.0000 | 0.0000 | 0.0000 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.5000 | 0.8750 | 0.8750 | 0.8750 | 0.6875 |
| difficulty | hard | 51 | 0.2195 | 0.3512 | 0.3902 | 0.4146 | 0.2894 |
| difficulty | medium | 41 | 0.3171 | 0.4390 | 0.4390 | 0.4634 | 0.3740 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

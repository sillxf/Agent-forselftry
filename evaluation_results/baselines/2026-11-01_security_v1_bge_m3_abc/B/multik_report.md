# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.5322 | 0.8556 | 0.8833 | 0.9556 | 0.2089 | 0.7148 | 0.7524 |
| parent | 0.5693 | 0.8833 | 0.9444 | 0.9778 | 0.2022 | 0.7448 | 0.7966 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.7333 | 0.9333 | 1.0000 | 1.0000 | 0.8356 |
| question_type | mixed_terms | 15 | 0.9333 | 0.9333 | 0.9333 | 1.0000 | 0.9333 |
| question_type | multi_document | 5 | 0.1667 | 0.9000 | 1.0000 | 1.0000 | 0.7000 |
| question_type | paraphrase | 15 | 0.6933 | 0.8667 | 0.8667 | 0.9333 | 0.8000 |
| question_type | technique_confusion | 15 | 0.6667 | 0.9333 | 0.9333 | 1.0000 | 0.7889 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.2000 | 0.8000 | 0.9600 | 0.9600 | 0.5267 |
| language_pair | en->en | 35 | 0.7781 | 0.9429 | 0.9714 | 1.0000 | 0.8867 |
| language_pair | en->mixed | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 0.9333 | 0.9333 | 0.9333 | 1.0000 | 0.9333 |
| language_pair | zh->en | 39 | 0.2308 | 0.8077 | 0.9231 | 0.9487 | 0.5385 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.6250 | 0.8750 | 1.0000 | 1.0000 | 0.7542 |
| difficulty | hard | 51 | 0.6398 | 0.9146 | 0.9512 | 0.9756 | 0.8069 |
| difficulty | medium | 41 | 0.4878 | 0.8537 | 0.9268 | 0.9756 | 0.6809 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

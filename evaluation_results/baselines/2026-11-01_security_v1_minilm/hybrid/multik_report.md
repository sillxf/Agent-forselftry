# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.3674 | 0.4389 | 0.4611 | 0.4861 | 0.1067 | 0.4217 | 0.4278 |
| parent | 0.4156 | 0.4806 | 0.5028 | 0.5583 | 0.1044 | 0.4593 | 0.4697 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.7333 | 0.8667 | 0.9333 | 1.0000 | 0.8056 |
| question_type | mixed_terms | 15 | 0.9333 | 0.9333 | 0.9333 | 0.9333 | 0.9333 |
| question_type | multi_document | 5 | 0.0000 | 0.0500 | 0.0500 | 0.0500 | 0.1000 |
| question_type | paraphrase | 15 | 0.8267 | 1.0000 | 1.0000 | 1.0000 | 0.9333 |
| question_type | technique_confusion | 15 | 0.0000 | 0.0000 | 0.0667 | 0.2000 | 0.0167 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.0000 | 0.0400 | 0.0400 | 0.1200 | 0.0200 |
| language_pair | en->en | 29 | 0.7724 | 0.9310 | 0.9655 | 1.0000 | 0.8649 |
| language_pair | en->mixed | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 0.9333 | 0.9333 | 0.9333 | 0.9333 | 0.9333 |
| language_pair | zh->en | 45 | 0.0000 | 0.0278 | 0.0500 | 0.1389 | 0.0278 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.5000 | 0.7500 | 0.8750 | 1.0000 | 0.6354 |
| difficulty | hard | 51 | 0.4000 | 0.4207 | 0.4451 | 0.4939 | 0.4329 |
| difficulty | medium | 41 | 0.4146 | 0.4878 | 0.4878 | 0.5366 | 0.4512 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.3407 | 0.4056 | 0.4167 | 0.4639 | 0.0978 | 0.3861 | 0.3914 |
| parent | 0.3889 | 0.4583 | 0.4917 | 0.5583 | 0.1022 | 0.4343 | 0.4488 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.6667 | 0.7333 | 0.8667 | 1.0000 | 0.7333 |
| question_type | mixed_terms | 15 | 0.8667 | 0.9333 | 0.9333 | 0.9333 | 0.8889 |
| question_type | multi_document | 5 | 0.0000 | 0.0500 | 0.0500 | 0.0500 | 0.1000 |
| question_type | paraphrase | 15 | 0.8000 | 1.0000 | 1.0000 | 1.0000 | 0.9000 |
| question_type | technique_confusion | 15 | 0.0000 | 0.0000 | 0.0667 | 0.2000 | 0.0167 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.0000 | 0.0400 | 0.0400 | 0.1200 | 0.0200 |
| language_pair | en->en | 29 | 0.7586 | 0.8621 | 0.9310 | 1.0000 | 0.8276 |
| language_pair | en->mixed | 1 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 0.8667 | 0.9333 | 0.9333 | 0.9333 | 0.8889 |
| language_pair | zh->en | 45 | 0.0000 | 0.0278 | 0.0500 | 0.1389 | 0.0278 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.6250 | 0.6250 | 0.7500 | 1.0000 | 0.6562 |
| difficulty | hard | 51 | 0.3659 | 0.4207 | 0.4451 | 0.4939 | 0.4085 |
| difficulty | medium | 41 | 0.3659 | 0.4634 | 0.4878 | 0.5366 | 0.4167 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

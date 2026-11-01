# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.3870 | 0.4722 | 0.4833 | 0.5194 | 0.1156 | 0.4454 | 0.4516 |
| parent | 0.4352 | 0.5250 | 0.5583 | 0.6028 | 0.1200 | 0.4954 | 0.5114 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.6667 | 0.7333 | 0.8667 | 1.0000 | 0.7333 |
| question_type | mixed_terms | 15 | 0.8667 | 0.9333 | 0.9333 | 0.9333 | 0.8889 |
| question_type | multi_document | 5 | 0.2333 | 0.4500 | 0.4500 | 0.4500 | 0.5000 |
| question_type | paraphrase | 15 | 0.6000 | 0.7333 | 0.7333 | 0.7333 | 0.6667 |
| question_type | technique_confusion | 15 | 0.4000 | 0.5333 | 0.6000 | 0.6000 | 0.4833 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.0000 | 0.0400 | 0.0400 | 0.1200 | 0.0200 |
| language_pair | en->en | 35 | 0.7476 | 0.8857 | 0.9429 | 1.0000 | 0.8429 |
| language_pair | en->mixed | 1 | 0.0000 | 1.0000 | 1.0000 | 1.0000 | 0.5000 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 0.8667 | 0.9333 | 0.9333 | 0.9333 | 0.8889 |
| language_pair | zh->en | 39 | 0.0000 | 0.0321 | 0.0577 | 0.1090 | 0.0321 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.6250 | 0.6250 | 0.7500 | 1.0000 | 0.6562 |
| difficulty | hard | 51 | 0.4675 | 0.5671 | 0.5915 | 0.5915 | 0.5427 |
| difficulty | medium | 41 | 0.3659 | 0.4634 | 0.4878 | 0.5366 | 0.4167 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.4026 | 0.5056 | 0.5278 | 0.5417 | 0.1244 | 0.4754 | 0.4848 |
| parent | 0.4619 | 0.5472 | 0.5694 | 0.6028 | 0.1222 | 0.5204 | 0.5323 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.7333 | 0.8667 | 0.9333 | 1.0000 | 0.8056 |
| question_type | mixed_terms | 15 | 0.9333 | 0.9333 | 0.9333 | 0.9333 | 0.9333 |
| question_type | multi_document | 5 | 0.2333 | 0.4500 | 0.4500 | 0.4500 | 0.5000 |
| question_type | paraphrase | 15 | 0.5600 | 0.7333 | 0.7333 | 0.7333 | 0.6667 |
| question_type | technique_confusion | 15 | 0.4667 | 0.5333 | 0.6000 | 0.6000 | 0.5167 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.0000 | 0.0400 | 0.0400 | 0.1200 | 0.0200 |
| language_pair | en->en | 35 | 0.7590 | 0.9429 | 0.9714 | 1.0000 | 0.8738 |
| language_pair | en->mixed | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 0.9333 | 0.9333 | 0.9333 | 0.9333 | 0.9333 |
| language_pair | zh->en | 39 | 0.0000 | 0.0321 | 0.0577 | 0.1090 | 0.0321 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.5000 | 0.7500 | 0.8750 | 1.0000 | 0.6354 |
| difficulty | hard | 51 | 0.5016 | 0.5671 | 0.5915 | 0.5915 | 0.5671 |
| difficulty | medium | 41 | 0.4146 | 0.4878 | 0.4878 | 0.5366 | 0.4512 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

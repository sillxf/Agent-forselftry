# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.4767 | 0.7815 | 0.8111 | 0.9000 | 0.1889 | 0.6448 | 0.6800 |
| parent | 0.5359 | 0.8056 | 0.8444 | 0.9778 | 0.1822 | 0.6807 | 0.7231 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.8667 | 0.9333 | 0.9333 | 1.0000 | 0.8889 |
| question_type | mixed_terms | 15 | 0.9333 | 0.9333 | 0.9333 | 1.0000 | 0.9333 |
| question_type | multi_document | 5 | 0.1667 | 0.9000 | 1.0000 | 1.0000 | 0.7000 |
| question_type | paraphrase | 15 | 0.4933 | 0.7333 | 0.7333 | 0.9333 | 0.6222 |
| question_type | technique_confusion | 15 | 0.6000 | 0.8000 | 0.9333 | 1.0000 | 0.7267 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.1600 | 0.6800 | 0.7200 | 0.9600 | 0.4080 |
| language_pair | en->en | 35 | 0.7495 | 0.9000 | 0.9143 | 1.0000 | 0.8476 |
| language_pair | en->mixed | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 0.9333 | 0.9333 | 0.9333 | 1.0000 | 0.9333 |
| language_pair | zh->en | 39 | 0.1795 | 0.6667 | 0.7436 | 0.9487 | 0.4256 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.7500 | 0.8750 | 0.8750 | 1.0000 | 0.7917 |
| difficulty | hard | 51 | 0.5667 | 0.8171 | 0.8780 | 0.9756 | 0.7252 |
| difficulty | medium | 41 | 0.4634 | 0.7805 | 0.8049 | 0.9756 | 0.6146 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

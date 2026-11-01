# Multi-K retrieval and grouped metrics

Candidate labels; no generated-answer accuracy or Agent refusal claim.

One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.

| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| child | 0.7711 | 0.9444 | 0.9556 | 1.0000 | 0.2267 | 0.8819 | 0.8944 |
| parent | 0.8304 | 0.9667 | 0.9889 | 1.0000 | 0.2111 | 0.9174 | 0.9354 |

## Groups (Parent metrics)

| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| question_type | english | 15 | 0.7333 | 0.9333 | 1.0000 | 1.0000 | 0.8356 |
| question_type | mixed_terms | 15 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| question_type | multi_document | 5 | 0.4667 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| question_type | paraphrase | 15 | 0.7600 | 0.8667 | 0.9333 | 1.0000 | 0.8467 |
| question_type | technique_confusion | 15 | 0.9333 | 1.0000 | 1.0000 | 1.0000 | 0.9667 |
| question_type | unanswerable | 10 | N/A | N/A | N/A | N/A | N/A |
| question_type | zh_to_en | 25 | 0.8400 | 1.0000 | 1.0000 | 1.0000 | 0.9133 |
| language_pair | en->en | 35 | 0.7781 | 0.9429 | 0.9714 | 1.0000 | 0.8867 |
| language_pair | en->mixed | 1 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | en->none | 4 | N/A | N/A | N/A | N/A | N/A |
| language_pair | mixed->en | 15 | 1.0000 | 1.0000 | 1.0000 | 1.0000 | 1.0000 |
| language_pair | zh->en | 39 | 0.8077 | 0.9744 | 1.0000 | 1.0000 | 0.9111 |
| language_pair | zh->none | 6 | N/A | N/A | N/A | N/A | N/A |
| difficulty | easy | 8 | 0.6250 | 0.8750 | 1.0000 | 1.0000 | 0.7542 |
| difficulty | hard | 51 | 0.8472 | 0.9756 | 1.0000 | 1.0000 | 0.9561 |
| difficulty | medium | 41 | 0.8537 | 0.9756 | 0.9756 | 1.0000 | 0.9106 |

Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate.

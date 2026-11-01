# 中文跨语言检索对照（候选结果）

原始题目未改变；翻译未混入主 Benchmark；人工审核仍未完成。

## Child Retrieval Metrics (K=5)

| Strategy | Group | Recall@5 | MRR@5 | NDCG@5 | Mean ms |
| --- | --- | ---: | ---: | ---: | ---: |
| dense | A | 0.0000 | 0.0000 | 0.0000 | 8.7012 |
| dense | B | 1.0000 | 1.0000 | 1.0000 | 8.5171 |
| dense | C | 1.0000 | 0.2667 | 0.4434 | 15.2484 |
| dense | D | 1.0000 | 0.7500 | 0.8155 | 17.6749 |
| bm25 | A | 0.0000 | 0.0000 | 0.0000 | 2.3664 |
| bm25 | B | 1.0000 | 1.0000 | 1.0000 | 1.1492 |
| bm25 | C | 0.0000 | 0.0000 | 0.0000 | 2.3824 |
| bm25 | D | 1.0000 | 0.5000 | 0.6309 | 3.6324 |
| hybrid | A | 0.0000 | 0.0000 | 0.0000 | 11.9704 |
| hybrid | B | 1.0000 | 1.0000 | 1.0000 | 10.1011 |
| hybrid | C | 0.0000 | 0.0000 | 0.0000 | 18.2196 |
| hybrid | D | 1.0000 | 0.2917 | 0.4653 | 22.7348 |

## Parent Retrieval Metrics (K=5)

| Strategy | Group | Recall@5 | MRR@5 | NDCG@5 | Mean ms |
| --- | --- | ---: | ---: | ---: | ---: |
| dense | A | 0.0000 | 0.0000 | 0.0000 | 8.7012 |
| dense | B | 1.0000 | 1.0000 | 1.0000 | 8.5171 |
| dense | C | 1.0000 | 0.2667 | 0.4434 | 15.2484 |
| dense | D | 1.0000 | 0.7500 | 0.8155 | 17.6749 |
| bm25 | A | 0.0000 | 0.0000 | 0.0000 | 2.3664 |
| bm25 | B | 1.0000 | 1.0000 | 1.0000 | 1.1492 |
| bm25 | C | 0.0000 | 0.0000 | 0.0000 | 2.3824 |
| bm25 | D | 1.0000 | 0.5000 | 0.6309 | 3.6324 |
| hybrid | A | 0.0000 | 0.0000 | 0.0000 | 11.9704 |
| hybrid | B | 1.0000 | 1.0000 | 1.0000 | 10.1011 |
| hybrid | C | 0.0000 | 0.0000 | 0.0000 | 18.2196 |
| hybrid | D | 1.0000 | 0.2917 | 0.4653 | 22.7348 |

## 解释边界

- Only two development questions; not a holdout or statistical significance test.
- Translations are precomputed, not online translation; translation latency/cost is NOT measured.
- D doubles candidate retrieval routes; no matched-compute quality claim.
- C preserves chunks rather than re-chunking for its tokenizer; long texts may truncate.
- BM25 does not embed; C BM25 is a sparse-control repeat of A.
- No production model, query policy, RRF or chunk settings are modified.

## 翻译语义检查

- rag_011: 保留本地/告警响应清单/哪些措施的范围；brute-force 是暴力破解的术语翻译，没有添加 IP、MFA 或其他答案词。尚需人工确认。
- rag_014: 保留本地/SQL 注入/预防措施的范围，没有添加 prepared statements 等答案词。尚需人工确认。

## 配置决定

结果只能支持下一轮更大样本的翻译/多语言/双路实验，不能证明生产全局最优。
不自动更换默认模型，不引入 Query Expansion 或 Reranker。
人工确认答案与翻译后，再用未参与调试的新问题验证收益、成本和语义偏差。

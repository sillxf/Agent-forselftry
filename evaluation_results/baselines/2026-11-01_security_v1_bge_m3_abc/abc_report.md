# Security RAG Benchmark V1：A/B/C 实测对比

A 为已封存的 MiniLM + Hybrid；B 为 BGE-M3 + 同一 Hybrid；C 为 BGE-M3 原问/英文双 Dense + 英文 BM25 + RRF60。

同一 100 题、21 份文档、301 个冻结 Child、70 个 Parent；没有修改 Benchmark 或 Ground Truth。
正文以 unique-Parent 的事实覆盖宏平均计分。90 道可回答题进入 Recall/MRR/NDCG；10 道不可答题不进入这些指标。

## 1. 全部可回答问题

| 方案 | Recall@5 | Recall@10 | MRR@5 | NDCG@5 | 查询错误 |
| --- | --- | --- | --- | --- | --- |
| A | 56.94% | 60.28% | 52.04% | 53.23% | 0 |
| B | 94.44% | 97.78% | 74.48% | 79.66% | 0 |
| C | 98.89% | 100.00% | 91.74% | 93.54% | 0 |

## 中文问题 → 英文文档（39 道可回答题，跨越主分类）

| 方案 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- |
| A | 5.77% | 10.90% | 3.21% |
| B | 92.31% | 94.87% | 53.85% |
| C | 100.00% | 100.00% | 91.11% |

## 英文问题 → 英文文档（35 道可回答题，跨越主分类）

| 方案 | Recall@5 | Recall@10 | MRR@5 |
| --- | --- | --- | --- |
| A | 97.14% | 100.00% | 87.38% |
| B | 97.14% | 100.00% | 88.67% |
| C | 97.14% | 100.00% | 88.67% |

## 中文跨语言相对 A 的变化

| 方案 | Recall@5 变化（百分点） | Recall@10 变化（百分点） | MRR@5 变化（百分点） |
| --- | --- | --- | --- |
| B | +86.54 | +83.97 | +50.64 |
| C | +94.23 | +89.10 | +87.91 |

## 检索耗时（毫秒/题）

| 方案 | 全 100 题 mean | p50 | p95 | 中文→英文 mean | 英文→英文 mean |
| --- | --- | --- | --- | --- | --- |
| A | 13.03 | 12.99 | 17.22 | 15.29 | 10.97 |
| B | 162.25 | 155.66 | 199.43 | 174.35 | 158.11 |
| C | 359.74 | 414.07 | 503.27 | 459.75 | 216.51 |

耗时是每题实际在线检索路径，不含 qrels 评分、模型下载/加载和建索引。C 使用已冻结英文 Query，不含翻译生成耗时；这是缓存翻译条件，不是端到端在线翻译性能。
A 为历史运行时间，B/C 为本次运行；后台负载和缓存可能不同。耗时不是受控并发压测，不据此宣称严格倍数。CPU/线程/依赖及 BGE 建索引、加载耗时见各组 config.json。

## C 仍失败的典型问题

90 道可回答题中，Top5 必要事实未全覆盖 1 题；Top10 零命中 0 题，未全覆盖 0 题。

### rag_009 — paraphrase

How can a tester infer database information when no data is returned directly?

- Parent Recall@5 / @10：0.00% / 100.00%；首个正向排名：6。
- 可确认现象：正确事实落在第 6–10 名。
- 各路标注正向 Child 排名：dense=16; bm25=2。
- 未覆盖事实来源：owasp_wstg_v4_2_sql_injection.md。
- Top5 来源：owasp_wstg_v4_2_sql_injection.md, owasp_wstg_v4_2_sql_injection.md, owasp_wstg_v4_2_sql_injection.md, owasp_wstg_v4_2_sql_injection.md, owasp_wstg_v4_2_sql_injection.md。


上述是从实际排名、证据匹配和已标注干扰来源得出的观察。仅凭排名不能确定模型语义、翻译或 Chunk 边界是哪一个根因；完整原文和排名见 C/retrieval_results.jsonl 与 C/failure_report.md。这里按冻结 Ground Truth 的标注引文严格计分，没有因其他段落看起来相关就临时扩充正向证据。

## 复现与边界

- Dataset SHA-256：`0d1c86f478883b3b385e01828f5fddc9ac37f6df44e7bcc955fc88bca4ef37e3`。
- BGE revision：`5617a9f61b028005a4858fdac845db406aefb181`。
- 模型、Tokenizer、Chunk/向量和源码 SHA 保存在 config.json；本次英文 Query 在 english_queries.json，逐题翻译调整记录在 translation_changes.json。
- 英文原问与英文翻译相同时去重 Dense 路由；非英文题通常是三路 RRF。
- BGE 仅使用 Dense 向量；BM25 仍是原有 BM25Plus，不是 BGE 原生稀疏或 ColBERT。
- 使用原 MiniLM 冻结 Chunk，控制切分变量；不代表 BGE 所有长文档配置的上限。
- 这仍是公开开发候选集（约 63 个去重文档+引文事实，含语言变体），不能把此处接近满分外推为生产或独立留出集表现。
- 标签仍为原候选审核状态，本次没有开展人工审核；没有生成答案、Cross-Encoder 或 Agent 拒答实验。
- 生产 app/、原 MiniLM 索引和原实验结果没有修改。

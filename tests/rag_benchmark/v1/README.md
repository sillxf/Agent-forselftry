# Security RAG Benchmark V1（100 题候选版）

主版本为 dataset/dataset.json 里的 r2，语言平衡修订见 design_revisions.json。

- 100 题、21 份资料；原 30 题核心内容和审核状态不变。
- 所有新题/实验翻译均 pending，无真实审核人签字。
- `dataset/questions.jsonl`：唯一题目和 Ground Truth 真值。
- `dataset/review.md`：逐题来源审核表；`dataset/coverage.json`：统计。
- `question_designs.json`、`evidence_designs.json`：设计输入；`evidence_catalog.json`：实际解析证据。
- `english_queries.json`：仅用于实验 C，原问与英文翻译逐题配对，不含参考答案或证据标签。
- `manifest.json`、`SOURCES.md`：冻结文档、原始版本、哈希与许可。
- `experiments.json`：A/B/C 定义与命令。

[完整运行指南与实际结果](../../../docs/rag_benchmark_expansion.md)

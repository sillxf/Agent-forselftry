# 应用代码与评测代码的边界

```text
app/
└── rag/                    # 生产解析、切分、索引、检索；不计算评测指标

evaluation/
├── rag/
│   ├── dataset.py          # 测试数据集与标注、语料一致性检查
│   ├── runner.py           # 逐题检索、证据映射、排名诊断
│   ├── metrics.py          # Recall、Precision、MRR、NDCG
│   ├── report.py           # 评测结果与报告
│   ├── benchmark.py        # 检索对照流程
│   ├── answer_review.py    # 真实 HTTP 路由检索 + 评测专用答案生成
│   ├── crosslingual.py     # 实验检索组合，不改变生产策略
│   ├── crosslingual_experiment.py
│   ├── analysis.py         # 失败归因
│   ├── audit.py            # 历史标注核查工具
│   └── provenance.py       # 模型指纹和源码快照
└── agent/                  # Agent 评测边界已预留，执行器和 Judge 尚未实现
```

## 依赖方向

- `app/` **不能导入** `evaluation/`、`scripts/` 或 `tests/`。
- `evaluation/` 可以调用 `app/` 的真实生产能力，不能反向导入命令脚本或测试夹具模块。
- `scripts/` 保留已有命令名称，评测入口只转发到 `evaluation/`，不再承载评分实现。
- `tests/` 验证生产与评测代码；固定文档、标注和 Agent 候选案例继续留在现有测试数据目录，避免无意义地改变数据路径及历史哈希。
- `evaluation_results/` 存输出，不作为生产知识库，也不作为应用导入模块。

生产 `/knowledge/search` 仍只负责检索；`answer_review.py` 的 LLM 生成是评测步骤，不是生产问答接口。
评测用独立进程和显式知识库/索引参数，不能在正在运行的生产进程里切换评测配置。

## 已有命令不变

```powershell
.\.venv\Scripts\python.exe scripts/run_rag_benchmark.py --retriever all --top-k 5 --offline
.\.venv\Scripts\python.exe scripts/run_rag_answer_review.py --offline-models --generate --top-k 3 `
  --output-dir evaluation_results/new-answer-review
```

也可以直接使用模块入口：

```powershell
.\.venv\Scripts\python.exe -m evaluation.rag.benchmark --help
.\.venv\Scripts\python.exe -m evaluation.rag.answer_review --help
```

新运行的源码快照包含 `app/`、`evaluation/`、`scripts/` 的 Python 文件及 requirements，
不包含 `.env`、API key 或模型权重。迁移前的封存结果不改写，仍使用它们原来的源码快照复现。
这次只是代码归属与导入路径调整，不改变生产策略、评分定义或既有开发参考分数。

## Agent 评测

规划见 [`agent/README.md`](agent/README.md)。未来的 `runner.py`、`judges.py`、`metrics.py`
应在 `evaluation/agent/` 实现，不能放进生产 Agent 或 RAG 包。目前不添加空实现来冒充完成。

## Security V1 扩展工具

- `rag/expansion.py`：固定来源节选、设计输入到标签的显式生成，拒绝覆盖已有 labels。
- `rag/coverage_audit.py`：旧集与新集覆盖审查、真实证据校验和未签字复核单。
- `rag/multik.py`：共享排名前缀的多 K/分组指标与失败、噪声诊断。
- `rag/model_comparison.py`：冻结 Chunk 的 A/B/C 实验；缺权重时明确记未运行。

这些模块不被 `app/` 导入；没有引入生产模型切换或 Cross-Encoder。

## 查询组件复用

生产查询组件在 `app/rag/retrieval/`，由 `RetrievalPipeline` 编排。
评测调用 `retriever.pipeline.rank_candidates()` 或直接组合公开 Dense/Sparse/Fusion/Context 组件，
不再调用 Retriever 私有召回/Parent 方法。冻结索引通过 `attach_index()` 一次绑定 store、documents、parents 和查询模型。
索引格式、评分协议和历史结果不因这次组件化改变。

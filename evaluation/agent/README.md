# Agent 小样例验收与离线复核

本目录已实现最小执行器，调用真实 `InvestigationService` 和只读工具，记录输入、
检索证据、模型请求与响应、工具结果、错误、耗时和服务端返回的 token 用量。
目标是检查实际链路和具体边界，不是宣称整体回答准确率提高。
模型输入保留完整告警 JSON，避免只传描述而丢失已知的 IP、时间、资产等字段。

## 入口和边界

- `runner.py`：运行案例、记录检索与 LLM 调用；参考答案和预期边界只进入报告，不进入模型输入。
- `judges.py`：检查结构和预算、提供复核提示；不靠关键词自动判定事实正确。
- `metrics.py`：分别统计执行结果、显式语义复核和已知用量；未知用量不算免费，未知账单不编造。
- `benchmark.py`：命令入口和报告；没有 `--live` 不会付费调用，`--replay` 不加载模型、不联网。

默认最多选 3 个案例、共 8 次请求，每次输出上限 4096 token、超时 90 秒，SDK 重试关闭。
次数预算包含失败请求，另有输入字符预算；这些是调用边界，不是精确美元费用预算。
生产 LLM 客户端默认行为不变，限制参数仅在显式传入时生效。
所有结果写到新目录，禁止覆盖旧报告；评测存储和输出不能与生产 `app/storage` 重叠。
运行时的告警池明确来自案例 fixture；例如空列表真的交给工具查询，不能伪造工具执行。

## 三个代表场景

使用已经构建好的**隔离存储**，或指定一个新的隔离存储（首次运行会构建）。
下面检查证据充分、证据不足、空工具结果，不重跑百题检索集：

```powershell
.venv\Scripts\python.exe scripts/run_agent_evaluation.py --live `
  --storage-dir evaluation_results/isolated-agent-storage `
  --output-dir evaluation_results/agent-smoke `
  --case-ids ae_001,ae_005,ae_008 --limit 3 --max-calls 8
```

`--live` 使用已配置的主 LLM，可能产生费用。不要在失败后无上限重试或扩大案例数。
可用 `--timeout`、`--max-completion-tokens`、`--max-input-chars` 进一步缩小范围。
若没有明确的服务商价格，报告保留 token 数和未知账单；可选价格参数只生成估算，不冒充实际扣费。

输出包括 `results.jsonl`（逐案例刷新）、`metadata.json`、`summary.json`、`review.md`、
`reviews.json` 和无凭据的代码快照。遇到配置、网络或全局调用预算错误会停止后续付费案例。
完整记录可能包含真实告警与知识内容，请当作内部资料，不提交到 Git。

## 离线复核

```powershell
.venv\Scripts\python.exe scripts/run_agent_evaluation.py `
  --replay evaluation_results/agent-smoke/results.jsonl `
  --reviews evaluation_results/agent-smoke/annotations.json `
  --output-dir evaluation_results/agent-reviewed
```

复核文件以案例 ID 为键，填写 `reviewer`、`reviewer_type`（`human` 或 `ai_development`），
以及 `dimensions` 下的 `alert_understanding`、`evidence_grounding`、`hallucination`、
`risk_assessment`、`response_quality`、`abstention`。每项均需 `verdict`（`pass`/`fail`/`uncertain`）
和基于实际记录的 `reason`。原运行的模型和来源元数据随重放保留，不归到新模型名下。

执行成功、结构正确和语义正确分开统计。未复核不算语义通过；AI 开发复核不是人工审批，
现有候选案例标签仍待人工审阅。退出码不替代逐条阅读复核结果。

## 旁路迁移工具

`scripts/run_rag_migration_acceptance.py` 接受显式的 `--baseline-ref` 和新 `--output-dir`，
默认只检查小型实际知识库，保存旧代码与完整隔离存储备份，演练损坏、删除、有效期和回滚。
**不切换生产，不默认选择百题数据集**。大规模基准只在显式指定 `--dataset` 时运行，
已有迁移结果应复用，不能因文档或评测代码的小改动重复执行。

现有设计见 [`docs/agent_evaluation_design.md`](../../docs/agent_evaluation_design.md)，
8 个候选案例仍在 `tests/agent_evaluation/cases.jsonl`。

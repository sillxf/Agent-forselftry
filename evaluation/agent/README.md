# Agent 评测（待实现）

这是 Agent 评测的代码边界，不是已经实现的自动评测器。

未来模块分工：

- `runner.py`：驱动生产 Agent 或只读回放，保存输入、输出、工具调用、错误和耗时。
- `judges.py`：对证据依据、事实归因、幻觉与拒答等给出可解释判断；LLM Judge 仅辅助。
- `metrics.py`：汇总各维度结果，不与 RAG 召回指标混用。

现有设计见 [`docs/agent_evaluation_design.md`](../../docs/agent_evaluation_design.md)，
8 个候选案例仍在 `tests/agent_evaluation/cases.jsonl`。
此处不放占位 runner、永远通过的 Judge 或固定返回零的指标。

# Agent 评测

入口是 `run.py`。默认模式为 dry-run：打印实际选中的 case id 和 split，不加载 Agent/RAG 客户端，也不调用模型。Live 模式必须显式提供全局请求上限、成本上限及由调用者确认的输入/输出价格上限；每个 case 最多 6 次模型请求。成本按每次最大 token 上限预留，达预算即停止。

## Dry-run（无模型、无网络）

~~~powershell
.\.venv\Scripts\python.exe -m benchmark.evaluation.agent.run --output "$env:TEMP\agent-dryrun"
~~~

默认选择当前全部 12 个案例。可用 `--case-ids ae_001,ae_002` 或 `--split development` 显式缩小范围，`--max-cases N` 只作为额外上限。

## Live（仅在确认预算后手动执行）

以下参数是占位符，不是价格建议；先按所用服务价格填写真实的正数预算。此示例只选一个案例，请求上限须覆盖最多 6 次调用，成本上限须覆盖请求数乘以单请求最大 token 费用。

~~~powershell
.\.venv\Scripts\python.exe -m benchmark.evaluation.agent.run `
  --live --case-ids ae_001 --max-cases 1 `
  --max-requests 6 --max-cost-usd <USD_BUDGET> `
  --input-cost-per-1m <USD_INPUT_PRICE> --output-cost-per-1m <USD_OUTPUT_PRICE> `
  --max-input-tokens-per-request 10000 --max-output-tokens-per-request 4096 `
  --output benchmark/runs/agent-<run-id>
~~~

Live 结果可在相同输入、模型和 prompt 指纹下续跑；运行文件只写脱敏后的诊断摘要与哈希，不写原始告警/证据载荷或密钥。工具轨迹检查是确定性子指标；观察/知识分类与提示注入抵抗需要语义判断时明确记为 `not_checked`，不能据此宣称通过。案例均为合成候选且无人类逐题审核，不能证明生产质量。

# Security Investigation Agent

agent/ 负责安全告警调查：整理告警、选择只读工具、控制调查预算、引用证据并校验报告。它通过 RAG 的 REST API 和只读 Key 获取知识，不直接访问 RAG 的数据库、原件或索引。

## 运行

配置 .env 中的 RAG_SERVICE_URL、RAG_SERVICE_TOKEN、RAG_SERVICE_KNOWLEDGE_BASES 和 LLM 配置后执行：

~~~powershell
.\\.venv\\Scripts\\python.exe -m agent
~~~

## 代码地图

- schemas.py：告警、证据和报告数据结构。
- tools.py、knowledge.py：RAG 检索和关联告警工具。
- triage.py、investigator.py：调查流程和模型调用。
- state.py、verify.py：状态管理、预算和报告校验。
- demo.py：本地演示入口。
- tests/：确定性测试。

Agent 评测在 benchmark/evaluation/agent/，真实模型运行必须显式开启，并将结果写入被忽略的 benchmark/runs/。

## 正式告警调查边界

正式入口是 `python -m agent`：CLI 读取调用者给出的告警 JSON 批次，按目标告警逐条创建一次性 `Investigator`；代码执行规则风险与批次内重复告警关联，随后由 `Toolbox` 完成初始 RAG 搜索，再进入单节点、有界 LLM/工具循环，最后由 `verify.py` 校验报告。`demo.py` 是独立的 DesignAdvisor 演示流程，不是告警调查入口，也不与告警调查测试结果合并解释。

RAG 仅通过 `RAGKnowledge` 调用 `POST /api/v1/search`，请求 `include_trace=true`，不导入服务端检索、存储或索引实现。每条知识搜索步骤记录可获得的 `request_id`、generation ID、knowledge-base configuration revision、证据 ID、引用摘要和服务 trace；响应未包含 trace 时记录 `trace_status=unavailable`，不把缺失 trace 表示为空 trace。检索结果会保留服务提供的 relevance 与来源类型，但 Agent 不设置通用 relevance 阈值，也不把分数解释为跨模型可比较的质量结论。

报告中的观测证据（`obs:`）来自输入告警、代码规则和只读工具结果；知识证据（`ev:`）来自本次 run 的 RAG 返回项。来源校验只确认引用 ID 属于本次调查，并检查证据类别，不验证引用内容是否语义蕴含该结论。未知来源、类型降级、confirmed 状态调整都保留在报告的 `verification` 中；运行记录另含校验规则版本及校验结果。

告警关联工具只在 CLI 调用者传入的批次内查找，不连接 SIEM、资产目录或身份日志。工具为只读白名单，参数由 schema 校验，且受模型调用、工具请求和知识搜索预算与重复调用保护；建议动作不会执行。运行 JSON 保留现有 `report`、`steps`、`observations`、`evidence`、`usage` 等字段，并增加 `run_record`。记录包含告警 ID/hash、规则风险、逐步状态/调用 ID/耗时/安全参数摘要、RAG trace、模型调用序号和用量、报告校验/降级和终态失败类别。为兼容现有输出策略，告警观测和检索证据正文仍会出现在 JSON 中；工具自由文本参数只保存长度/hash 等摘要，凭据、Authorization header 与 provider 原始错误不写入结果。

`--output <path>` 保存本次调查 JSON，未指定时 JSON 输出到 stdout。它是已完成调查的记录，不代表任务可暂停、取消或跨进程恢复；CLI 调查退出后不支持从该文件恢复执行。失败检索状态（如 `timeout`、`not_published`、`index_damaged`、`not_authorized`、`busy`）与成功的 `empty` 结果分开记录；当服务以成功响应报告部分知识库未发布时，记录 `partial`/`partial_empty` 与未发布知识库，而不会伪装为完整空检索。服务故障不能解释为“没有相关攻击/知识”。

## 验证与评估

确定性检查：

~~~powershell
.\.venv\Scripts\python.exe -m unittest discover -s agent/tests -p "test_*.py"
~~~

现有 Agent benchmark 是显式 `--live` 的模型冒烟，不在本次实现或单元测试中自动运行。人工决定启动前，可先用不调用模型的 dry-run 检查案例范围：

~~~powershell
.\.venv\Scripts\python.exe -m benchmark.evaluation.agent.run --output benchmark/runs/agent-dry-run
~~~

实际模型评测需明确设置 `--live` 并写入被忽略的 `benchmark/runs/`。它有费用且最多每案例 6 次模型请求；当前案例状态与自动诊断不足以代表整体质量，仍需按 benchmark README 做人工逐案复核。本任务没有触发 live benchmark，也没有改动 benchmark 输入或评测代码。

RAG 兼容性建议：成功搜索响应应稳定提供 `request_id`，并在 trace 或响应元数据中提供每个知识库对应的 generation ID；trace、citation 可缺失，但应在输出中明确标记缺失状态。若服务错误响应已有 request ID/generation ID，建议作为稳定可选字段提供，Agent 会只采集这些诊断字段，不保存错误正文或请求头。

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

# AI 协作任务书

本目录包含项目任务书和 AI 协作工作区。三个执行 AI 分别负责 `benchmark/`、`RAG/`、`agent/`；代码应在独立 worktree/分支中修改。各 AI 的计划和报告统一写入 `workspace/cycles/<cycle_id>/`，协调 AI 可直接读取，不需要用户在对话间复制粘贴报告。

## 项目目标

把 `D:\AI-SecOps-Agent` 建设成一个可解释、可回放、可评测的安全告警 Agent 与独立 RAG 服务，并用自动化 benchmark 判断改动是否有效。

## 当前基线（2026-11-14）

- `RAG/` 已有独立 REST/MCP 服务、文档解析与分块、增量索引、发布快照、混合检索、任务控制和检索 trace。
- `agent/` 已有安全告警调查主流程、只读工具、调用预算、步骤记录和报告来源校验。Agent 通过 REST 访问 RAG，不应直接访问其存储。
- `benchmark/` 已有 100 道 RAG 候选题、12 个合成 Agent 案例、检索实验和答案级评测入口；当前样本都是待审核或未执行状态，不能当作经过人工审核的真实质量结论。
- Agent 运行状态目前主要在单次进程内；RAG Worker 重启时会把未完成任务标记为 interrupted，要求显式重试，不承诺从崩溃指令处恢复。

## 三个任务与写入边界

1. `01-benchmark.md`：仅负责 `benchmark/`。建设不依赖人工逐题审核的机器生成、机器校验与 AI 裁决流程。
2. `02-rag.md`：仅负责 `RAG/`。改善 RAG 的证据质量、发布/失败可解释性和 REST 检索观测；不修改 Agent 或 benchmark。
3. `03-agent.md`：仅负责 `agent/`。改善告警调查的证据链、检索 trace 与可回放输出；不修改 RAG 内部实现或 benchmark。

根目录配置、共享 API 契约和 benchmark 数据格式属于共享边界。代码写入范围隔离不代表共享契约没有依赖；需要改变共享契约时，由协调 AI 在计划中指定唯一负责人并冻结契约，再安排消费者适配。除非任务确实无法完成，不要改根目录配置；若必须改，先在计划中说明理由和最小方案。

## 建议启动顺序

- 先更新 `workspace/CURRENT.md`，记录本轮目标、轮次 ID、状态和代码基线；每个新轮次使用新的 ID，保留旧轮次记录。
- 各 AI 在项目目录中打开独立对话，按角色启动对应任务书。任务书会要求读取 `workspace/CURRENT.md`，并将产物写入其中指定的轮次目录。
- 执行 AI 可并行的前提是代码写入范围不同、共享契约冻结。每个 AI 使用独立 worktree/分支；报告写到主项目共享路径 `ai-work-orders/workspace/cycles/<cycle_id>/`。
- 完成后，协调 AI 直接读取三个报告和各自代码差异，写验收报告。不要让执行 AI 自动合并或覆盖其他任务的修改。

## 共享接口契约（保持兼容）

- Agent 是调用方，只通过 RAG REST API 获取知识；禁止导入 RAG 内部检索、数据库、FAISS、原件或索引模块。
- 现有检索入口是 `POST /api/v1/search`。请求支持 `query`、可选 `queries`、`knowledge_base_ids`、`top_k`、`min_score` 和 `include_trace`。
- 响应包含 `request_id`、`results`、元数据和证据引用；请求 `include_trace=true` 时可返回检索 trace。结果还可携带发布代次及文档/版本/chunk/page 引用。
- RAG 可增加向后兼容的字段；不得无协商移除或改义现有字段。Agent 应在 trace 不可用时优雅退化，不把“缺少 trace”伪装成“没有证据”。
- Benchmark 通过公开 API 或被评测对象的正式入口运行；不可读取 RAG 私有数据库/向量索引来获得不公平答案。

## 如何开启各角色对话

无需复制整份任务书或手动转交其他 AI 的报告。每个 AI 都在项目目录中打开自己的对话，然后发送对应的一行启动指令：

```text
请按 ai-work-orders/01-benchmark.md 和 workspace/CURRENT.md 当前状态处理本轮任务，并将报告写入其指定路径。
请按 ai-work-orders/02-rag.md 和 workspace/CURRENT.md 当前状态处理本轮任务，并将报告写入其指定路径。
请按 ai-work-orders/03-agent.md 和 workspace/CURRENT.md 当前状态处理本轮任务，并将报告写入其指定路径。
请执行 ai-work-orders/04-coordinator.md，读取 workspace/CURRENT.md 和轮次报告，按当前状态完成计划或验收并保存到指定路径。
```

只有 `CURRENT.md` 指定 `status: planning` 时启动协调 AI 产出计划；代码完成后设为 `acceptance` 再启动协调 AI 验收。完成后由 Architect 将状态设为 `complete`。任务边界见 `04-coordinator.md`，模板和当前轮次见 `workspace/README.md`、`workspace/CURRENT.md`。

> 本方案不要求你逐题人工标注 benchmark，但 AI 自动裁决的数据不能被描述为“人工审核真值”。报告中必须展示机器裁决方法、置信度、模型/提示版本、分歧率和未决比例。

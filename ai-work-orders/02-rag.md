# 任务 02：RAG 服务证据质量与生产可解释性

## 轮次状态

启动时先读 `ai-work-orders/workspace/CURRENT.md`。`status: implementation` 才执行本任务的代码修改；`status: acceptance` 时只基于当前对话已有工作和可访问差异补齐执行报告，不得继续开发。若历史成果或差异不可访问，如实说明，不要编造。

## 目标

在保留现有 REST/MCP 服务边界的前提下，提高 RAG 文档处理与检索的可诊断性、证据可追溯性和发布可靠性。优先完善现有实现，不重写已有管线，也不在没有大规模压测证据时宣称支持 TB 级语料。

## 当前基础

RAG 已有 Docling 解析、结构恢复、跨页合并、父子分块、增量构建、Embedding 缓存、SQLite/FAISS 快照、发布回滚、混合检索/RRF/重排、权限过滤和任务 pause/resume/cancel。索引 Worker 重启后将运行中的任务标成 `interrupted` 并要求显式 retry；不应宣传成崩溃点续跑。

主要位置：`RAG/app/ingestion/`、`RAG/app/indexing/`、`RAG/app/retrieval/`、`RAG/app/storage/`、`RAG/app/permissions/` 和 `RAG/tests/`。

## 范围

仅修改 `RAG/` 下文件。先检查当前 API 契约、错误模型、索引发布与现有测试，然后选最有价值的缺口实现；避免把所有面试题都扩展成新系统。

1. 文档管线可定位：文档版本/来源 hash、解析与结构质量状态、各处理阶段、错误类别和任务 ID 之间有稳定关联。解析失败或可疑结构应能被管理方发现，不能无提示地作为高质量证据发布。
2. 检索证据可追溯：检索响应可在调用方请求时提供 request ID、索引 generation、配置 revision、候选数量、检索路线/重排/回退状态和来源引用；trace 中不暴露密钥、原始敏感令牌或不必要的全文。
3. 发布安全：新构建未成功前旧 generation 继续提供服务；发布切换原子/受保护；失败、取消或暂停不会留下对外可见的半成品快照。沿用当前任务状态语义，向调用方明确 queued/running/paused/interrupted/succeeded/failed/cancelled 的区别。
4. 任务恢复表述与行为一致：区分安全检查点 pause/resume 与进程重启后的 interrupted/retry。只有实现并验证持久检查点后才可称断点续跑；不要为追求表面功能而盲目重放高成本操作。
5. 权限必须在服务端执行，包括多知识库检索、版本/删除操作；不要依赖 Agent 的 Prompt 过滤。沿用最小权限与当前 actor 认证语义。
6. 用确定性小型测试验证最关键路径：文档坏输入/结构告警、搜索 trace/citation/generation、旧版本持续服务、取消/发布互斥、权限拒绝。只针对实际修改路径增补测试。
7. 核对 RAG 的在线/离线链路：说明输入、产物、版本/hash、失败/回放能力。优先为已有能力补清晰契约和错误定位，不另建重复的任务或索引框架。

## 兼容性与协作约束

- 共享 REST 契约详见 `README.md`。`POST /api/v1/search` 的现有请求和响应字段必须向后兼容。若新增字段应为可选；`include_trace=true` 是调用方获取诊断信息的 opt-in。
- Agent 仅通过 REST 使用知识。禁止要求 Agent 导入 `RAG/app` 私有实现。
- Benchmark 将通过正式 API/公开入口评测，不能只为某评测器增加内部捷径。
- 不改 `agent/`、`benchmark/` 或根目录配置。若必须修改共享契约，在交付中列出变更、兼容性和消费者迁移建议。

## 非目标

- 不将本地 SQLite/FAISS 架构包装成已验证的 TB 级方案。
- 不改成多 Agent 或生成式 RAG 服务；RAG 返回证据，不负责最终业务调查报告。
- 不引入消息队列、分布式租约服务、云向量数据库等新基础设施，除非现有实现证明必要且任务范围允许。
- 不对无关模块做大规模重构，也不运行大额模型/全语料压测。

## 实施步骤

1. 先检查当前根 `AGENTS.md`、RAG README、API schema、索引发布代码和对应测试。
2. 选最多 2–3 个与“证据正确且可追踪”直接相关的缺口，解释选择理由。
3. 在 RAG 范围内实现最小兼容改动；确保旧发布快照在新构建失败时保持有效。
4. 为改动路径补充确定性测试，运行 RAG 对应测试集并报告明确命令与结果；不因小改动跑无关全仓测试。
5. 更新 RAG 内部说明：行为边界、任务状态、trace 字段、已知限制。

## 验收标准

- Agent 和 Benchmark 可继续只用现有 REST 契约访问；没有消费者必须读取 RAG 内部文件。
- API 返回的证据引用足以定位知识库、文档/版本、chunk、页码和 generation（在字段适用时）；trace 可用于区分检索路线、重排、回退和空结果。
- 解析/索引错误带有安全、可操作的类别和关联对象，日志/响应不会泄露 token 或 provider secret。
- 当前 generation 在新构建中、构建失败和取消时仍符合一致的发布规则；不得返回已删除/失效对象的陈旧证据。
- pause/resume、restart/interrupted 和 retry 语义通过对应确定性测试，文档不夸大恢复保证。
- 变更涉及的 `RAG/tests/` 测试通过；不相关测试未运行时说明原因。
- 未声称尚未测量的生产准确率、吞吐、延迟或 TB 级能力。

## 交付报告

列出修改文件、选择的缺口、API/schema 变化、任务与发布语义、测试命令/结果、尚未解决的质量/规模限制。不得修改 Agent 或 Benchmark 文件。

完整报告必须写入 `workspace/CURRENT.md` 中 `rag_report` 指定的共享路径，使用 `workspace/templates/execution-report.md` 作为补充格式。即使代码在独立 worktree 中修改，也要将报告写入主项目共享工作区；对话回复只需简述结论和报告路径。不得覆盖其他角色的报告。

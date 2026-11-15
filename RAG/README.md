# RAG 知识服务

RAG/ 是独立的知识库管理与证据检索服务。它负责知识库和文档生命周期、解析分块、索引构建与发布、检索、权限、REST API、管理台和 MCP 接入。

## 运行

从仓库根目录执行：

~~~powershell
.\\.venv\\Scripts\\python.exe -m app init
.\\.venv\\Scripts\\python.exe -m app serve --port 8090
.\\.venv\\Scripts\\python.exe -m app worker
~~~

前端源码在 RAG/frontend/，构建产物位于 RAG/app/web/，由 API 服务提供。Windows 用户可直接双击根目录的 启动.cmd。

## 代码地图

- app/api/：HTTP 路由、请求模型和控制台会话。
- app/knowledge/：知识库、文档、版本和生命周期。
- app/ingestion/：文件加载、解析、版面处理和分块。
- app/indexing/：构建、发布、任务控制和 Worker。
- app/retrieval/：检索、融合、过滤和上下文组装。
- app/models/：Embedding、Reranker、LLM 和模型配置。
- app/storage/：数据库、快照和向量存储。
- mcp_server/：面向 MCP 客户端的协议工具。
- tests/：RAG 服务确定性测试。

app 是安装后的 Python 包名，源码目录保留在 RAG/app/。Agent 与 RAG 的边界是 REST API；不要在 Agent 中直接导入 RAG 的内部存储或检索实现。

## 证据追踪与任务边界

`POST /api/v1/search` 保持原有请求和结果字段兼容；调用方将 `include_trace` 设为 `true` 后，响应中的 `request_id` 会同时出现在每个知识库的 trace 中。每条 trace 包含知识库 ID、配置 revision、generation、检索/上下文候选数量、响应入选数、响应预算与 top-k 排除数、检索路线、重排状态和回退原因。零结果原因区分无候选、单库上下文预算、跨库响应预算、top-k 截断和生命周期过滤；结果包含 generation、文档/版本、chunk 与页码引用。trace 只返回结构化诊断字段，不包含 provider secret、认证令牌或原始全文。

构建先生成未发布快照，只有在发布保护区内完成代际校验后才切换 current pointer。构建失败、取消或暂停不会把半成品变成对外 generation；旧 generation 会继续服务。`queued`、`running`、`paused`、`interrupted`、`succeeded`、`failed` 和 `cancelled` 是不同状态：pause/resume 只覆盖任务检查点，Worker 进程重启会把运行中任务标为 `interrupted`，需要显式 retry，当前不承诺进程级断点续跑。

文档解析失败会使本次构建失败并保留旧发布；Docling 和结构恢复产生的结构信息会进入块与构建产物。当前 API 尚未提供独立的文档质量告警列表或“可疑但可发布”的管理审核状态，因此不能把结构恢复成功等同于解析质量已验证。生产准确率、吞吐、延迟和 TB 级规模均未在本项目中测量或承诺。

## 检查

~~~powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s RAG/tests -p "test_*.py"
~~~

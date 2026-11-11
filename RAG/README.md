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

## 检查

~~~powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s RAG/tests -p "test_*.py"
~~~

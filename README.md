# 知序 · Independent RAG

独立的知识库管理与证据检索服务（`app/`），本身不生成答案。

同一仓库另有一个基于它的安全告警调查 Agent（`agent/`），只通过 REST API 和只读 Key 使用 RAG 服务，见下文“安全调查 Agent”。两者可以分开部署。

## Windows 双击启动

本机已安装依赖后，双击根目录 **启动.cmd**：自动启动网页服务和后台处理程序，服务就绪后打开浏览器并自动进入本地管理台，无需输入令牌。重复双击会复用现有服务。双击 **停止.cmd** 可停止这组进程，关闭浏览器不会停止服务。

首次一键启动保留旧构建、清理任务的排队状态，标注“待确认执行”，由你在“任务与发布”确认后再运行；历史永久删除任务标为未执行，不会自动删除。后续新提交的构建正常由后台执行；文档和知识库的删除直接生效。停止时正在处理的任务可能中断，再次启动后需核对并明确重试。

启动读取 .env 中的 RAG_SERVICE_DATA，默认数据仍在 storage。日志位于数据目录 logs/。端口被其他程序占用时会弹出错误，不会擅自停止其他程序。本地管理台使用浏览器会话自动连接；外部 API 和 MCP 仍使用令牌鉴权，令牌不会放入浏览器 URL。缺少 .venv 或依赖时按下面步骤完成一次安装。

## 首次安装 / 命令行启动

Python 3.11+。首次使用本地模型/解析器可能下载模型。修改前端另需 Node.js 22。

~~~powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -e .
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\.venv\Scripts\python.exe -m app init
.\.venv\Scripts\python.exe -m app serve --port 8090
# 另一个终端，使用相同数据目录与模型/凭据环境：
.\.venv\Scripts\python.exe -m app worker
~~~

打开 http://127.0.0.1:8090/ 。管理员令牌从 storage/admin.token 读取，不要放进 URL 或提交 Git。

安装后也可使用 rag-service。数据默认只有根 storage 一处；用 --data 或 RAG_SERVICE_DATA 指定其他位置，API、Worker 和运维命令必须保持一致。

## 项目结构

~~~text
frontend/src/
  app/                 页面外壳、会话与知识库选择
  api/                 HTTP 客户端
  features/            功能自己的页面、状态与操作
  shared/              展示组件、通用资源读取
app/
  main.py, cli.py      启动和命令入口
  bootstrap.py         唯一组件装配入口，不提供业务转发方法
  api/                 HTTP 路由、请求模型、认证依赖
  core/                配置、公共契约、异常、输出脱敏
  knowledge/           知识库、文档、版本、生命周期、检查
  ingestion/           文档解析、结构处理、分块
  indexing/            构建、发布、回滚、清理、任务与 Worker
  retrieval/           只读查询、策略、过滤、融合、上下文
  models/              模型配置、模型池、Embedding/Reranker/生成适配器
  permissions/         Key、授权范围与查询配额
  audit/               有界审计记录
  storage/             数据库、向量、索引快照读写代码
  web/                 前端构建产物，不手工修改
mcp_server/            只读 MCP 协议和工具
migrations/            显式离线迁移、备份、恢复
storage/               运行数据，Git 忽略
scripts/               源码导出，不含第二套管理命令
tests/                 一次有界的服务可用性检查
evaluation/            可选纯指标计算，不运行实验
docker/, docs/         部署与说明
~~~

依赖方向：入口 → 对应领域服务 → 管道组件 → 存储/模型适配器。

没有同时负责构建和查询的全能 Runtime，没有转发所有操作的总 Service。构建由 Worker 显式执行，查询只加载已发布索引。前端只共享会话与知识库选择，业务状态由各功能持有。

## 使用闭环

创建知识库 → 上传文档 → 配置模型与构建参数 → 构建发布 → 调试检索 → 创建限定知识库的只读 Key。

支持 Dense、BM25、Hybrid、可选重排（本地或远程 /rerank 服务）、调用方明确请求的 Multi-View 补检，以及调用方提供的多查询融合（queries，例如补一条文档语言的翻译）；支持文档版本、软删除/恢复、有效期、复核日期、新文档取代旧文档、硬清理、索引回滚、备份恢复。返回原文、引用身份与可选检索轨迹，上下文按 token 计预算，不判断业务证据是否充分，不自动生成答案。

首版是单主机模块化单体：一个 API、一个 Worker，SQLite + FAISS + BM25 + 托管文件。两个进程的模型内存需要合计预算。

详见 [结构说明](docs/architecture.md) 与 [运维说明](docs/operations.md)。

## 安全调查 Agent

输入一条告警和同批告警，输出结构化调查报告：观察事实、参考知识、推断、未验证假设、缺失数据和建议。确定的步骤（输入校验、规则风险分、去重、首次检索、预算、报告校验）由代码完成；模型只决定调用哪个只读工具（同批告警查询、知识检索、读取证据原文）并撰写报告。每条陈述必须引用本次运行中真实存在的来源，否则由代码降级为未验证假设；建议永远标记为未执行。设计见 [docs/agent_design.md](docs/agent_design.md)。

~~~powershell
# .env 中配置 LLM_API_KEY / LLM_BASE_URL / LLM_MODEL，
# 以及 RAG_SERVICE_URL、只读 Key RAG_SERVICE_TOKEN、RAG_SERVICE_KNOWLEDGE_BASES
.\.venv\Scripts\python.exe -m agent agent\examples\sample_alerts.json --alert-id AL-001
~~~

每条告警最多 6 次模型请求、12 次工具调用、3 次知识检索。8 个合成案例的真实模型冒烟结果和 AI 开发复核见 [evaluation/agent/README.md](evaluation/agent/README.md)。

## 开发和必要检查

~~~powershell
# 前端修改完成后统一构建，写入 app/web：
cd frontend
npm ci
npm run build
cd ..
# 完整功能批次后按需检查一次，不调用付费模型、不跑效果实验：
python -m unittest discover -s tests -p "test_*.py"
python -m tests.smoke
~~~

改动分块、向量模型或检索策略时，用冻结基准跑一次效果对比，不必每次都跑：见 [evaluation/README.md](evaluation/README.md)。答案是否正确、是否会拒答，用 [答案级评测](evaluation/answer/README.md)，题目需要人工审核。容量问题用 scripts/load_test.py 实测；扩容路径见运维说明。

Docker：docker compose up --build -d，默认仅映射本机 8090。对外发布需要 HTTPS、可信 Host/Origin、数据卷备份及资源限制。

源码导出：python scripts/export_product.py <新的源码包.zip>，包含源码、文档和检查脚本，不含数据、凭据、模型、依赖缓存或历史报告。

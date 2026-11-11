# 知序 · 独立 RAG Knowledge Service

## 产品边界

这是独立安装、独立运行的证据检索服务，不是安全 Agent 的一个页面，也不是自动问答或工作流平台。安全 Agent 通过 HTTP 客户端调用；其他程序可用 REST 或只读 MCP。服务不判断业务证据是否充分，不自动回答问题，不默认执行效果实验。

首版是**单主机、受信任管理员、多个受限调用方**的模块化单体。SQLite、FAISS、BM25、本地文件继续使用；一个 API 进程、一个 Worker 进程，共享本地磁盘。不是多租户 SaaS，不支持多主机共享网络文件系统或多个 API/Worker 写入进程。对互联网开放前必须配置 HTTPS、允许的 Host/Origin 和部署层连接/带宽限制。

## 安装与启动

推荐 Python 3.12。项目根目录执行：

~~~powershell
npm ci --prefix frontend
npm run build --prefix frontend
python -m pip install .
python -m rag_service --data ./rag-data init
python -m rag_service --data ./rag-data serve --port 8090
# 第二个终端，使用相同数据目录和模型/凭据环境：
python -m rag_service --data ./rag-data worker
~~~

管理台位于 http://127.0.0.1:8090/ 。init 不调用模型；它生成管理员令牌文件 rag-data/admin.token 和默认知识库。令牌不输出到日志，请从文件读取。限制该目录的操作系统访问权限，Windows 上应配置账户 ACL。可用环境变量 RAG_SERVICE_ADMIN_TOKEN 替代文件，至少 24 字符。网页令牌只保存在页面内存，不写 localStorage。管理员是受信任主体，不应把管理员令牌交给 Agent。

前端源码在 frontend；构建结果随 Python 包一起发布。后端不依赖原 app 目录。Vite 开发服务默认代理 8090，因同源限制，开发时另设 RAG_ALLOWED_ORIGINS=http://localhost:5173 。生产推荐同源部署。

## 日常闭环

1. 在管理台创建知识库。
2. 上传文档；上传只冻结原件和版本，不偷偷建索引。
3. 根据需要设置元数据、有效期、文档级 View 生成选项。
4. 点击“构建并发布”，由 Worker 处理。旧发布继续提供检索。
5. 查看任务进度、文档解析 Markdown、Parent/Child、目录和 View。
6. 在检索调试台检查来源、候选、重排前后与阶段耗时。
7. 给调用方创建绑定知识库的只读 Key，接入 REST 或 MCP。

文件支持沿用已有 MD/Markdown、PDF、DOCX、XLSX、PPTX、HTML、常见图片；PDF/OCR 依赖模型。默认上传 25 MiB。原件只作为附件下载，解析 Markdown 使用纯文本预览，不在服务域执行上传的 HTML。文档/Chunk 检查支持分页，Markdown 预览超过 200,000 字符明确标记截断；原件仍完整保留。

## 组件与数据边界

~~~text
rag_service/
  api.py, mcp.py           REST / MCP 适配，复用同一个应用服务
  service.py              授权、查询、文档检查、配置与任务协调
  contracts.py            BuildConfig / RetrievalProfile / SearchRequest
  catalog.py              多库目录、模型配置、Key 摘要、任务与审计
  providers.py            本地/兼容 HTTP Embedding、本地 Reranker、模型池
  worker.py               持久化任务，独立进程运行
  maintenance.py          离线迁移、备份与恢复
  client.py               轻量 HTTP 客户端，不导入检索/解析核心
  core/                   从现有项目抽离的唯一 RAG 实现
    ingestion/ processing/ chunking/
    indexing/ retrieval/ lifecycle/
  web/                    生产管理台静态资源
~~~

前端按七个业务页面拆分在 frontend/src/pages；App.tsx 只负责工作台外壳，useConsoleController.ts 集中共享会话、知识库选择和 API 协调，shared.tsx 保存轻量展示组件。页面通过显式类型契约取得所需能力，不另造通用工作流框架。

app/rag 保留旧 Python 导入兼容入口，不维护第二份算法。新增组件通过构造注入和类型契约加入；不提供任意 Python 动态加载、插件市场或拖拽工作流。

每个知识库有独立 Registry、原件、索引代际和发布指针；同进程模型池由多个库共享，默认最多加载 3 个模型。API 和 Worker 分别持有各自模型池，因此部署资源预算须同时考虑两个进程。本地模型忙时容量等待默认 5 秒，不无限排队。FAISS 元数据过滤在最终 Top-K 选择前执行；过滤路径采用本地精确向量子集计算，会有随候选规模增长的内存/计算成本。大规模过滤需求再考虑远端后端，不假装已有 Qdrant 适配。

## 构建配置与在线策略

- IndexBuildConfig：Embedding 版本、Parent/Child token、重叠、OCR。变更后构建新代际，原子发布。
- RetrievalProfile：Dense / BM25 / Hybrid / Hybrid+Rerank、候选量、输出量、上下文预算、补检开关、Parent Context。新请求使用新策略。
- SearchRequest：查询、明确的知识库范围、元数据过滤、受限模式、是否明确补检、可选 as_of。
- SearchResponse：原始证据、引用、版本、索引代际、配置修订、分阶段分数、降级原因，可选 Trace。

模型配置不可原地修改；新增配置产生新 ID，索引签名绑定该 ID，完整配置随目录数据库持久化。构建期间修改构建配置会阻止旧任务发布。Embedding、维度、归一化、距离、前缀、query/document 编码、模型修订共同决定向量空间。维度和有限数值会验证；远端服务是否在同名模型下偷偷换权重无法由本服务证明，管理员应使用不可变版本并登记新配置。

已发布查询、历史查询和回滚跟随索引绑定的 Embedding，而不是最新填写的期望模型。模型停用禁止新配置和构建，但保留旧索引读取。Reranker 变更不重建向量。当前距离统一 cosine，使用归一化内积；没有通用的 0.5 阈值，也不把 RRF/BM25/重排分数当概率。

初始 Provider：本地 Sentence Transformers、兼容 /embeddings HTTP 的远端 Embedding、本地 CrossEncoder Reranker。远端 Embedding 要指定维度与 tokenizer；凭据只保存环境变量名，真实密钥由运行环境注入。远端接口会接收文档/查询文本，启用前需接受相应数据外发边界。管理员可手动确认一次推理探测；保存配置和启动服务都不自动探测或收费。

多库查询最多显式指定 5 个授权库，按各库自己的模型和策略检索，再按库内名次融合；不是比较不同模型的原始分数，也不声称它等价于全局重排。最终总输出默认受 24,000 字符约束。首版不做 LLM 自动选库。

## Multi-View

三个独立控制面：文档是否离线生成、知识库是否允许查询、本次调用是否明确补检。默认关闭。mode=high_recall 是调用方的显式补检请求，不是内部质量判断。一次请求对每个所选库最多一次补充；View 必须映射回 canonical Child，补充融合后有界重排，失败保留主检索并返回原因。

管理台支持文档级模型名、批量、请求上限、超时、输出 Token 上限和失败策略。生成使用 RAG_VIEW_LLM_API_KEY / RAG_VIEW_LLM_BASE_URL / RAG_VIEW_LLM_MODEL；兼容继承原 LLM 环境变量。当前提示词固定 question-view-v1，生成中英问题。停用生成并构建会从新快照移除 View，不删除原始 Child；旧快照和可复用缓存按保留/清理规则管理。

全构建 View 请求上限 RAG_VIEW_MAX_REQUESTS_PER_BUILD 默认 8，按文档也有上限。兼容 HTTP Embedding 单操作默认最多 128 请求、2,000,000 输入字符，分别由 RAG_REMOTE_MAX_REQUESTS_PER_OPERATION、RAG_REMOTE_MAX_INPUT_CHARS_PER_OPERATION 配置。预检超限拒绝本批次，不自动重试外部请求。记录实际请求数和供应商返回 Token，用量缺失时不编造费用。

## 权限、API 与 MCP

所有 /api/v1 和 /mcp 请求必须携带 Authorization: Bearer <token>；管理静态页面本身不包含敏感数据。受限 Key 只读，绑定知识库；不能修改模型、任务或文档。Key 只显示一次，服务只保存摘要。每 Key 的 requests_per_minute 目前定义为**检索请求额度**，不是所有元数据 GET 请求计数；另有全局检索并发限制。撤销立即影响后续请求。已开始请求不保证立即撤销，客户端已经收到的内容无法追回。

授权在选择知识库前生效，文档、Chunk、原件、历史检索同样受库范围限制。无权库请求明确拒绝，不偷偷忽略。首版无库内文档级 ACL；同一库的授权调用方可读取该库证据。不要混放需要不同权限的文档。

主要 REST 路径：

- GET /api/v1/knowledge-bases；POST /api/v1/search
- GET/POST /api/v1/knowledge-bases/{id}/documents（上传为原始请求体，filename 参数）
- GET/PATCH/DELETE .../documents/{document_id}
- POST .../documents/{document_id}/undelete、restore-version；PUT .../validity
- GET .../documents/{document_id}/original/{version_id}
- GET .../chunks/{chunk_id}
- GET/POST /api/v1/models；PUT /models/{id}/enabled；POST /models/{id}/probe?confirm=true
- GET/POST /api/v1/keys；DELETE /keys/{id}
- POST .../jobs；GET /api/v1/jobs；POST /jobs/{id}/retry
- GET .../generations；GET /api/v1/audit
- GET /api/v1/openapi.json（管理员，完整请求 Schema）

~~~json
{"query":"如何处理登录失败告警？","knowledge_base_ids":["填写真实知识库ID"],"top_k":5,"supplement":false,"filters":{"metadata.domain":"security"},"include_trace":true}
~~~

返回 results 的 citation 包含知识库、文档、版本、Chunk、页码；generation_id 可用于后续 get_document / get_chunk 固定同一证据快照。as_of 是记录的历史发布，不是未发布编辑或历史检索策略重演；元数据过滤使用当前 Registry 元数据。删除、到期与 purge 边界沿用生命周期实现。历史快照已被回收/撤销时明确失败，不退回最新版本。

MCP 端点 /mcp/，Streamable HTTP；工具只有 rag_search、rag_list_knowledge_bases、rag_list_documents、rag_get_document、rag_get_chunk、rag_get_document_outline。没有暴露构建、删除或模型控制。stdio 使用轻量启动器代理同一个 HTTP 服务：

~~~powershell
$env:RAG_SERVICE_URL="http://127.0.0.1:8090"
$env:RAG_SERVICE_TOKEN="填写受限Key"
python -m rag_service mcp-stdio
~~~

Agent 客户端选择 HTTP 或 stdio 时，需按实际客户端版本配置鉴权、协议和传输；不声称已经在用户尚未指定版本的外部 Agent 客户端中逐个实测。传输协议链路会做本地集成验证。远程 Host 用 RAG_ALLOWED_HOSTS（逗号分隔，无端口）显式配置；额外 Origin 用 RAG_ALLOWED_ORIGINS 配置。不默认允许通配来源。Bearer 令牌部署适合受控调用方；未实现面向第三方用户的完整 OAuth 授权服务/动态注册。

## 原安全 Agent 接入

.env 配置 RAG_SERVICE_URL、RAG_SERVICE_TOKEN、RAG_SERVICE_KNOWLEDGE_BASES。Agent 默认不再启动本地 RAG 写入或挂载管理 API。没有配置时，知识调用明确报未配置而不是隐式建索引。兼容旧版可显式设置 RAG_EMBEDDED_MODE=true，但不得指向已切换到服务管理的数据目录。

## 任务与生命周期

任务有持久化状态、阶段和结果。提交支持 Idempotency-Key，重复同输入返回同任务；不同输入复用 Key 拒绝。Worker 单写者锁避免重复执行；API 与 Worker 是两个运行角色，不是微服务集群。重启发现 running 会标 interrupted，不自动重放可能收费的步骤。人工重试使用当前期望配置，复用已有缓存；不保证中断的外部请求只计费一次。检查已发布快照/生成记录后再决定是否重试。

软删除立即禁止当前检索；恢复与单文档内容版本选择继续支持。硬清理必须显式确认、可按持久化计划重试。清理会撤销包含文档的**整个旧快照**，因此可能影响其他文档的历史访问；当前其他文档不删除。不清理外部原件、外部备份、下载副本、其他存储根、物理介质或已发出的内存副本。

## 迁移、备份、恢复与升级

迁移前停止原 Agent 服务/CLI 写入者；不要双写。

~~~powershell
python -m rag_service --data ./rag-data migrate-legacy --knowledge ./app/knowledge --storage ./app/storage --backup D:/RAG-backups/pre-product --writers-stopped
~~~

迁移复制原件、Registry 和完整索引历史，重定位受管路径，重新校验清单；不重编号文档/版本/Chunk，不调用模型或重新做效果评测。备份含旧存储与原件，仓库可用时额外保存迁移前 HEAD 代码归档。成功后原存储写入 service-cutover.json 标记；新兼容入口拒绝继续把它当写入目录。--writers-stopped 是操作者确认，不能代替停止仍运行的旧版本程序。迁移失败保留备份和中间目录供排查，不冒险自动删除。

备份/恢复必须停止 API 和 Worker；工具会尝试获得两个进程锁，服务仍运行时拒绝。备份包含完整目录、SQLite 一致性副本、原始文件和 SHA-256 清单；可能包含管理员令牌，需按敏感数据保护。恢复只写全新目录，校验清单并重定位路径，禁止覆盖正在使用的数据。

~~~powershell
python -m rag_service --data ./rag-data backup D:/RAG-backups/service-v1
python -m rag_service restore D:/RAG-backups/service-v1 D:/RAG-restored
python -m rag_service --data D:/RAG-restored serve
~~~

这不是加密备份、增量备份或物理介质安全擦除。升级先备份并记录代码/包版本，再停写升级；不兼容升级回退应恢复匹配的旧代码与旧数据到新目录，而不是用旧代码打开新 Schema。运行时状态默认不进 Git。

## Docker 与独立交付

~~~powershell
docker compose -f deploy/compose.yaml up --build -d
docker compose -f deploy/compose.yaml exec api cat /data/admin.token
~~~

默认只绑定 127.0.0.1:8090；init 初始化卷，API/Worker 共享数据和模型缓存。生产外网访问应由 HTTPS 反向代理提供，并显式配置 Host/Origin。模型和生成密钥环境需同时传给会使用它们的 API/Worker；不应写进镜像。容器无 CUDA 配置，GPU 部署需自行配合相应 PyTorch/驱动镜像。

根 pyproject 只打包 rag_service，不打包安全 Agent。scripts/export_rag_product.py 可导出独立产品源码包，包含前端、部署和文档，不含凭据、数据、node_modules 或旧 app。可直接搬到独立仓库；本次不会擅自替用户创建新的远端仓库。

## 验证与未声称事项

按完整功能批次验证；高风险重点为跨库授权、删除、发布、模型切换、迁移和恢复。不会默认跑百题，不用小样例声称效果提升，不默认调用付费模型。交付报告记录实际通过/失败修复/跳过/环境限制。

本版不包含远端向量后端、多租户计费、自动连接器/文件监听、自动 LLM 路由、质量评测平台、OAuth 平台或通用问答界面。这些属于未来按实际需求扩展，不作为本轮隐藏任务。

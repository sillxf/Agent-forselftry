# 通用知识库：管理、版本与检索

> 新产品入口见 [RAG_PRODUCT.md](RAG_PRODUCT.md)。本文件描述兼容的嵌入式用法；完成独立服务迁移后，不再对旧存储执行这些写入命令。安全 Agent 默认通过 HTTP 客户端接入；嵌入式模式需显式启用。

安全 Agent 是该 RAG 的调用方之一。核心不判断业务证据是否充分，也不生成通用问答答案。本版本不包含多租户权限平台、跨知识库路由或检索效果实验。

## 启动和入口

在仓库目录使用 `.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000`。

- 管理页面：`/knowledge/admin`。
- 管理 API：文档、索引、任务和策略，见 `/docs` 的 knowledge 分组。
- 普通检索：`GET /knowledge/search?q=问题&k=3&include_trace=true`。
- 明确请求补检：在上述请求中加 `supplement=true`。默认关闭，需要管理员先启用策略并构建文档 View。
- 历史查询：加 `as_of=2026-11-03T08:00:00Z`（替换为实际记录的发布时间）。需要管理员访问权限。

普通检索只读已发布快照，HTTP 冷启动不会自动构建或迁移。需要先手动构建；构建失败仍使用上一份可用发布。Python `KnowledgeRetriever` 保留兼容的自动构建默认值，需要只读部署时设置 `auto_build=False`。

未设置 `RAG_ADMIN_TOKEN` 时，管理操作和历史查询仅允许回环地址；设置后使用 `Authorization: Bearer <token>`，页面令牌只保存在当前页面内存。拒绝跨域管理请求。远程部署应使用 HTTPS/反向代理，公开检索的访问控制由部署层负责；这不是租户隔离系统。

## 日常操作

1. 上传文档，或更新已有文档。上传采用原始文件请求体，文件名是查询参数 `filename`，不是 multipart；更新时带 `document_id`。默认大小上限 25 MiB，可通过 `RAG_UPLOAD_MAX_BYTES` 调整。
2. 设置分类、领域、来源、生效/过期时间，以及是否生成 Question Views。
3. 点击“构建并发布”。任务在后台运行，旧发布继续服务；刷新查看结果和错误。
4. 用少量实际查询确认所需资料能被检索。此操作不构成效果评测。

支持现有 MD/Markdown、PDF、DOCX、XLSX、PPTX、HTML 和常见图片；没有顺带扩展 TXT/CSV。PDF/OCR 所需本地模型仍按现有配置安装。

文档状态与发布状态分开：上传/选择版本并不代表已经发布。有效期和软删除会立即限制在线检索，不需要等待重建。

## 文档级 View

`ViewConfig` 示例：

```json
{"enabled":true,"model":"你的生成模型","batch_size":8,"max_requests":8,"max_completion_tokens":2048,"timeout_seconds":90,"failure_policy":"publish_without_views"}
```

- 默认关闭；只有文档明确启用后，离线构建才可能调用付费生成模型。
- 独立环境变量：`RAG_VIEW_LLM_API_KEY`、`RAG_VIEW_LLM_BASE_URL`、`RAG_VIEW_LLM_MODEL`；未设置时兼容使用现有 LLM 配置。凭据不会进入文档配置和快照。
- `RAG_VIEW_MAX_REQUESTS_PER_BUILD` 默认 8；会预先检查本次所有待生成文档的请求数，超预算不启动付费生成。还有每文档请求数、单次输出和超时上限，无 SDK 自动重试。
- 缓存绑定文档 ID、内容版本、处理产物、模型、提示词版本和生成配置。修改文档/配置后旧产物标记过期，不关联到新内容。
- 记录状态、错误、请求数与供应商实际返回的 token 用量；没有供应商报告的用量不冒充已知费用。
- `publish_without_views`：生成失败仍可发布普通检索；`fail_build`：中止发布，保留旧快照。
- 做结构、重复、原文身份/内容哈希校验，不声称规则能保证问题的语义忠实性。不运行效果实验、自动答案打分或额外语义审查模型。

提示词目前只支持已实现的 `question-view-v1`，不接受任意不存在的版本标签。

## 调用方控制补检

默认 Hybrid（可配置 Hybrid + 精排）。只有调用方明确传入 `supplement=true` 才尝试一次补检：映射原文 → 合并去重 → 强制精排。未启用、缺少 View、精排忙/超时/失败时保留第一轮结果，trace 明确原因，不将失败说成无资料。

安全 Agent 仅在策略启用后看到 `knowledge_supplement` 工具，每次调查最多一次，并受原有查询、工具调用和证据长度预算约束。普通 `knowledge_search` 不开放任意策略选择。核心没有 SufficiencyChecker，也不会为判断充分性另调 LLM。

## 历史版本与时间点

- 内容版本不可变；恢复是选择某个旧版本并在下一次构建中重新发布，不篡改历史。
- 使用版本固定选择，不覆盖用户原始文件；原始文件丢失时仍可用保存的源字节构建。后续明确的源内容变化会解除固定选择。
- `as_of` 定义为“当时最近一次已记录发布的知识”，不是重建每一次未发布修改，也不是重演当时的检索模型/策略。使用当前检索策略检索历史证据。
- 历史生命周期边界来自快照中记录的有效期；当前软删除不抹掉过去，但硬删除对全部时间点生效。
- 回滚也作为一次新的发布记录。只有从当前原子指针可达的发布链算已发布，构建中断产生的孤立文件不会混入历史。
- 原格式未记录的时间点、已 GC 或硬删除的快照明确不可用，不偷偷改查最新资料。

## 增量与发布

本版本使用格式 8 快照和 Registry schema 4。

- 未变文档直接复用已发布文档/块，不重新解析、切块或编码。
- FAISS 在私有副本上移除旧块、加入新块；BM25 的词频、倒排集合及总长度增量维护，按当前语料统计计算 IDF。
- 每份发布仍有完整独立快照、校验和与原子指针。索引计算增量不等于零复制，保存快照仍有磁盘/序列化开销。
- 模型、处理配置变化或 `rebuild --full` 按需要全量构建。全量重建也可用于主动修复一次性缓存。
- 本次没有引入向量数据库、消息队列或通用工作流系统。

## 软删除、硬删除和恢复边界

软删除可取消，查询即时过滤。硬删除必须显式确认：

1. 持久化清理计划，设置永久禁止提供标记，阻止自动再导入。
2. 发布不含目标文档的新快照。
3. 撤销包含目标内容的旧快照及其回滚/恢复资格，然后移除它们。
4. 清理受管理的源版本、解析/切块/View 产物、图片及无引用的向量缓存；共享字节仍被其他逻辑文档引用时保留。
5. 清除 Registry 历史，使用 SQLite secure_delete 和 VACUUM；记录清理完成。

`purged_at` 表示已永久停止提供，不等于物理清理完成；管理 API 的 `purge_state` 和页面会区分清理失败/未完成与已完成。中断可对同一文档再次执行 purge，按持久化计划继续。失败状态不表示已经清理成功，但目标内容不会重新对外提供。

范围是该知识库配置的 storage，以及 knowledge-dir 内由其管理的原文件。**用户外部原始文件、其他独立知识库、应用外备份、已下载副本、内存物理擦除与 SSD 安全擦除不在范围内。** 外部原文件保留但阻止自动再导入。已载入内存的旧检索器通过权威 Registry 禁止继续返回目标文档。

硬删除会让同一旧快照里的其他文档也失去该快照的历史查询能力，但它们的当前内容不删除。这是优先彻底清理内容、同时保持实现简单的明确取舍。

## CLI

```powershell
.venv\Scripts\python.exe scripts/rag_documents.py list
.venv\Scripts\python.exe scripts/rag_documents.py import C:\资料\manual.md
.venv\Scripts\python.exe scripts/rag_documents.py configure DOCUMENT_ID --metadata-json '{"domain":"general"}' --views-json '{"enabled":false}'
.venv\Scripts\python.exe scripts/rag_documents.py rebuild
.venv\Scripts\python.exe scripts/rag_documents.py restore-version DOCUMENT_ID VERSION_ID
.venv\Scripts\python.exe scripts/rag_documents.py search "问题" --as-of "实际发布时间"
.venv\Scripts\python.exe scripts/rag_documents.py purge DOCUMENT_ID --confirm
.venv\Scripts\python.exe scripts/rag_documents.py generations
```

其他已有命令：versions、delete、restore、validity、rename、jobs、rollback、gc。CLI 是受信任的本地管理员入口；导入外部路径属于明确授权，HTTP 不接受任意服务器路径或 URL 抓取。

## 显式迁移和灾难恢复

先停止服务与写入者，再运行：

```powershell
.venv\Scripts\python.exe scripts/migrate_rag_storage.py --apply --backup-dir "新的备份目录" --legacy-code-ref "与当前旧数据匹配的Git版本"
```

脚本先复制完整 storage、knowledge，使用 SQLite backup 获取一致注册表，并保存指定旧代码的 ZIP、文件 SHA-256 清单，再构建发布。失败时不自动删除现场或伪装回滚成功。

恢复旧格式必须停服务，把备份的整套 storage/knowledge 放回原配置位置，并运行配套旧代码；不要只修改 current.json。可先将当前目录完整保留在另一个明确命名的位置，避免覆盖和丢失故障现场。备份含旧内容，硬删除后若有合规清除需求，也必须单独处理这些备份。

## 验证原则

只做功能闭环、边界和恢复验证；普通修改集中到交付节点。高风险删除/发布/迁移做针对性验证。复用原有结果，不启动百题、策略效果比较或付费质量实验。验证结果和运行备份不提交 Git。

# 运维

配置放环境或 .env；模型配置只引用 secret_env 名称，不保存密钥值。根 storage 是数据，app/storage 是代码。

API 与 Worker 使用同一数据根和模型/凭据环境。管理员受信任；外部应用使用限定知识库的只读 Key。网页令牌仅存在页面内存。

每库有独立 Registry、原件、版本、派生文件、索引代际和发布指针。改 Embedding/分块需新建并发布快照；改在线策略对新请求生效。回滚绑定目标快照模型。

上传不自动构建。Worker 校验后发布，过期任务不得覆盖新配置。中断任务标记 interrupted，由管理员显式重试，不自动重放可能收费的调用。

软删除/有效期影响可见性。硬清理不可直接恢复，并撤销相关历史；旧代际清理不等于原件硬清理。

备份前停止 API 和 Worker。使用 rag-service --data ./storage backup <新备份目录>；恢复使用 rag-service restore <备份目录> <新数据目录>。命令检查锁、校验备份，恢复到新目录，不覆盖活动数据。不是加密备份或介质安全擦除。旧单库迁移见 migrate-legacy --help，必须停写并指定外部备份。

检索接口 POST /api/v1/search，输入 query、knowledge_base_ids、top_k；按需提供 filters、as_of、include_trace、supplement。调用方自行判断业务证据是否充分。

HTTP MCP 位于 /mcp；stdio 使用 rag-service mcp-stdio 或 python -m mcp_server.server，通过 RAG_SERVICE_URL/TOKEN 连接同一 REST 服务，不能绕过权限。

Multi-View 默认关闭；启用文档级生成后构建可能收费。生成预算、超时与失败策略有界；模型 probe 必须显式 confirm=true，不在启动时执行。API、Worker 的模型内存分别计入预算。

这是单主机服务，不是多租户 SaaS 或自动问答平台。未实际运行 Docker 时不得声称容器部署通过；本地链路检查不代表远端付费模型都经过实测。

已缓存的本地模型优先按本地快照路径加载，不为每次进程首次查询强制联网检查。未缓存的新模型仍按显式配置正常下载；需要固定版本时设置模型 revision。

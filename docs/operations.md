# 运维

配置放环境或 .env；模型配置只引用 secret_env 名称，不保存密钥值。根 storage 是数据，app/storage 是代码。

API 与 Worker 使用同一数据根和模型/凭据环境。管理员受信任；外部应用使用限定知识库的只读 Key。网页令牌仅存在页面内存。

每库有独立 Registry、原件、版本、派生文件、索引代际和发布指针。改 Embedding/分块需新建并发布快照；改在线策略对新请求生效。回滚绑定目标快照模型。

上传不自动构建。Worker 校验后发布，过期任务不得覆盖新配置。中断任务标记 interrupted，由管理员显式重试，不自动重放可能收费的调用。

文档“删除”直接执行，不依赖 Worker：DELETE /api/v1/knowledge-bases/{kb_id}/documents/{document_id}?confirm=true，成功返回 200/status=completed 时，服务内原件、版本、相关索引和缓存已清理，文档不再出现在列表与检索中。不可恢复；包含它的旧快照也会撤销，外部原件与备份不在范围内。删除不加载模型或调用付费服务，未构建的上传文档也可以直接删除。失败时显示“删除未完成”，可重复请求恢复清理；构建等维护正在占锁时返回 409，不排队。

可恢复操作改为“移入回收站”：POST .../documents/{document_id}/trash；恢复仍为 POST .../undelete。为避免旧客户端误删，未带 confirm=true 的 DELETE 会被拒绝，不再代表软删除。新的 purge 任务提交被拒绝，使用直接删除接口；既有队列仍兼容，直接删除成功会将同一文档尚未执行的旧 purge 任务标为完成，不执行其他待办。旧代际清理不等于文档删除。

备份前停止 API 和 Worker。使用 rag-service --data ./storage backup <新备份目录>；恢复使用 rag-service restore <备份目录> <新数据目录>。命令检查锁、校验备份，恢复到新目录，不覆盖活动数据。不是加密备份或介质安全擦除。旧单库迁移见 migrate-legacy --help，必须停写并指定外部备份。

检索接口 POST /api/v1/search，输入 query、knowledge_base_ids、top_k；按需提供 filters、as_of、include_trace、supplement。调用方自行判断业务证据是否充分。

HTTP MCP 位于 /mcp；stdio 使用 rag-service mcp-stdio 或 python -m mcp_server.server，通过 RAG_SERVICE_URL/TOKEN 连接同一 REST 服务，不能绕过权限。

Multi-View 默认关闭；启用文档级生成后构建可能收费。生成预算、超时与失败策略有界；模型 probe 必须显式 confirm=true，不在启动时执行。API、Worker 的模型内存分别计入预算。

这是单主机服务，不是多租户 SaaS 或自动问答平台。未实际运行 Docker 时不得声称容器部署通过；本地链路检查不代表远端付费模型都经过实测。

已缓存的本地模型优先按本地快照路径加载，不为每次进程首次查询强制联网检查。未缓存的新模型仍按显式配置正常下载；需要固定版本时设置模型 revision。

知识库也支持直接删除：DELETE /api/v1/knowledge-bases/{kb_id}?confirm=true。总览的每个知识库及配置页均有“删除知识库”入口。删除整个库的受管数据目录、任务和 Key 授权范围；仅授权该库的 Key 自动撤销，共用模型、其他库、外部原件与备份不删除。正在执行维护时返回 409，不排队。清理失败时持久化 deleting 状态、停止该库读写，列表显示“删除未完成”供重试；删除最后一个知识库后可以重新创建。

每库维护锁位于数据根 locks/，与即将删除的目录分离；文档写入、Worker 和直接删除共用此门闩，检索不持有维护锁。更新此版本须同时重启 API 和 Worker，不能混用新旧写入进程。

删除与检索并发时，检索在返回前再次核对知识库及文档的实时可见性，过滤已删除文档；知识库已删除或处于删除失败状态时不返回成功检索结果。缓存 Registry 每次打开数据库前校验所属库状态，已初始化的数据库只以“不创建”方式打开，防止旧句柄复活已删除目录。文档清理失败也会刷新列表，显示“删除未完成 / 重试删除”。

Windows 根目录“启动.cmd / 停止.cmd”调用 scripts/desktop.ps1，只管理本目录创建且 PID、创建时间、完整命令行均匹配的进程。API 与 Worker 隐藏运行，日志和进程记录保存在数据目录；启动前检查端口，网页与 Worker 均就绪后才打开浏览器。首次使用该入口记录时间分界，旧构建和清理任务保留 queued 状态且不执行，管理台标注“待确认执行”，管理员明确确认后才执行；旧 purge 标记 interrupted，不自动删除。此后新提交任务正常执行。不自动安装依赖或调用模型探测。可在命令行以 -NoBrowser -Quiet 验证，-Port 指定测试端口。停止会终止所属进程树，正在执行任务可能中断。

本地双击入口以 serve --local-console 启动，只允许绑定回环地址。页面自动通过同源 POST 建立 HttpOnly、SameSite=Strict 的进程内会话，无需复制管理员令牌；令牌不会发到浏览器、URL 或本地存储。会话认证要求回环客户端、回环 Host、自定义请求头和同源校验；不接受外部来源的会话申请，不替代 MCP/Bearer 鉴权。退出或服务重启后会话失效。普通 serve 默认保留令牌模式，远程监听与 --local-console 不能同时使用。本机其他程序本来就属于受信任使用者，回环工作台不提供本机多用户隔离。

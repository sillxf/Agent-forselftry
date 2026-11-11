# 职责与扩展

bootstrap.create_services 是唯一装配入口，只创建依赖并返回命名服务集合。只有协议/命令入口使用集合；领域服务不接收整个应用对象。

- knowledge 管知识库配置、文档身份、版本、生命周期与原文检查。Workspace 只是数据句柄，不执行查询或构建。
- ingestion 管解析、结构恢复、分块，不发布索引。
- indexing 管任务与构建发布。IndexBuilder 只保存本次构建状态，不提供 search；任务中断不自动重放付费工作。
- retrieval 的 QuerySession 只加载已发布快照，不能构建或发布。PipelineFactory 在查询加载与发布前校验时共用。
- models 管不可变模型定义、适配器及每进程有界模型池。查询模型绑定快照，不能因新构建配置改变向量空间。
- storage 管数据库连接、快照和向量读写。SQL 归对应领域 Repository，不再有万能 Catalog。
- permissions/audit 统一授权、配额与审计；原始查询不进审计。

Multi-View 的生成/辅助索引归 indexing，模型调用归 models，检索归 retrieval，文档开关归 knowledge。

前端 app/context 只共享会话、当前知识库、提示与刷新信号。各 features 的 hook 自己持有局部状态；未挂载功能不继续读取业务数据。shared/useResource 只处理请求生命周期。

新解析器放 ingestion；新模型适配器放 models；新检索策略放 retrieval/strategies。使用类型契约和显式构造注入，不引入任意代码插件、工作流框架或微服务。

旧 Agent、兼容树、重复脚本与历史报告已移除，不承诺旧内部 Python 导入路径兼容；REST /api/v1、MCP 工具名及主要 CLI 操作保持不变。

新的调查 Agent 在顶层 `agent/`，是 RAG 服务的普通客户端：只通过 REST API 和限定知识库的只读 Key 检索，不导入 retrieval、indexing 或 storage，因此服务端的权限、配额和审计同样适用。它只复用 `app/models/llm/client.py` 这个无状态的 OpenAI 兼容客户端。`app/` 不依赖 `agent/`。设计见 agent_design.md。

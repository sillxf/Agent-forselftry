# 可组合 AI 团队平台：完整落实方案

- 轮次 ID：`2026-11-15-agent-team-platform`
- 决策文件：`ai-work-orders/workspace/cycles/2026-11-15-agent-team-platform/decision.md`
- 代码基线：分支 `feat/secops-agent`，HEAD `19059c2eae01d68552683d2789e998348992adb6`（2026-11-15 读取）；工作区有大量未提交修改。
- 总体建议：新增 `team_platform/` Python 应用边界，采用本地优先的模块化单体；旧安全调查 Agent 保持独立兼容，RAG 继续作为可选 REST 知识服务，Benchmark 继续独立评测，不合并或整体替换。
- 计划状态：待 Architect/用户批准；本计划不构成开发授权。

## 1. 当前结构与迁移策略

| 区域 | 当前职责/入口 | 对新平台的处理 |
|---|---|---|
| `RAG/app/`、`RAG/frontend/`、`RAG/mcp_server/` | FastAPI 服务、SQLite/FAISS 知识生命周期与检索；React 19/Vite 管理台；REST/MCP 边界 | 原样保留。平台只通过公开 REST 调用；MCP 继续服务 MCP 客户端，不作为 Agent 委派协议或平台必需依赖。仅在确认公开 API 缺字段时提出最小兼容变更。 |
| `agent/` | `python -m agent` 调用 `Investigator` 对告警批次逐条运行；状态/预算主要在进程内；工具、告警 schema、报告校验偏安全调查领域 | 作为旧产品入口和领域实现保留，不直接承载任意角色。先为新平台定义通用 Role Runtime；现有调查器是否封装为兼容角色留到 MVP 后评估。 |
| `benchmark/` | 冻结数据、答案/Agent/检索实验及数据契约、校验、dry-run、机器裁决 | 继续隔离，不作为角色专业评级系统。不得把候选集或词面指标宣传为能力认证。 |
| `tests/` | 根级跨边界 smoke | 只放 API/REST/包边界等跨模块检查；平台单测归 `team_platform/tests/`。 |
| 根 `pyproject.toml` | distribution 仍名 `rag-knowledge-service`；包发现跨 `RAG/` 和根目录，脚本主要服务 RAG | 接入平台时审查 package discovery、console script 和依赖，不把平台塞入 RAG 的 `app` 包，也不未经验证重命名发行包。 |
| 根 `启动.cmd` / `停止.cmd` | 当前启动/停止 RAG API 与 Worker | 保持行为不变。平台先用独立 CLI；确认体验后再新增平台入口，不隐式启动多个系统。 |

### 未提交改动与基线风险

- 当前只有共享工作树 `D:/AI-SecOps-Agent`，无隔离 worktree；分支 `feat/secops-agent`，HEAD 如上。`git status` 显示 RAG、Agent、Benchmark 都有已修改文件，还有未跟踪的 `benchmark/datasets/security-v1-r3/`、校验/裁决代码和测试及工作区材料。
- 这些差异来自 `2026-11-14-current-batch`，不属于新平台授权。旧轮次 `acceptance.md` 仍是模板；Agent 有复核报告，但 Benchmark/RAG 报告仍为占位内容。不得默认为已正式验收，不得 reset、清理、改写或混入新方向。
- 新轮次 `plan.md` 原先只有模板标题；本计划只替换该占位文件，旧轮次材料与产品代码均不动。
- 实现前硬门禁：Architect 先决定旧批次如何归档/验收，并指定新平台基线及隔离 worktree。不要在当前脏工作树直接开发，也不要自动复制所有未提交差异。仅在明确批准后逐文件确认需携带内容。
- 另有边界耦合：`agent/__main__.py`、`agent/demo.py` 从 `app.models.llm.*` 导入模型实现，而 `app` 实际是 `RAG/app` 包；新平台不得延续此导入。新平台自有模型端口/适配器；旧 CLI 的迁移需独立决策。

### 迁移原则

1. 新建并列平台包；第一版不重构 RAG，也不将旧 `agent/` 改名。
2. 跨模块只共享冻结的数据/API 契约；禁止导入 RAG 的检索、数据库、模型或 Worker 私有实现。
3. 迁移以适配器/显式兼容层完成；旧 CLI、旧 JSON 输出和 RAG 管理台保持可运行。
4. 修改根 `pyproject.toml`、启动入口、RAG API 或跨模块测试的工作作为单独集成任务，串行实施并回归。

## 2. 推荐架构与职责目录

首版采用**一个产品模块、一个本地数据边界、一个 API 进程和一个有界 Worker**的模块化单体；API 与 Worker 从同一代码包以不同命令启动，SQLite 是共享持久层。不引入消息队列、微服务、远程 Agent 或多租户集群。初始 Worker 并发建议为 1，证明持久化/取消语义后再调整。

建议目录：

```text
team_platform/
  __init__.py / __main__.py / composition.py
  api/{application.py,routes/,schemas/}
  domain/{packages/,roles/,teams/,runs/,permissions/}
  orchestration/{planner.py,dispatcher.py,state_machine.py,coordinator.py}
  runtime/{executor.py,model_protocol.py,providers/,prompt_assembly.py}
  connectors/{registry.py,project_files.py,rag_rest.py}
  persistence/{database.py,migrations/,repositories/}
  services/{package_service.py,team_service.py,run_service.py,artifact_service.py}
  frontend/                    # 独立 React/TypeScript/Vite 源码
  web/                          # API 同源托管的构建资产（若采用）
  examples/role-packs/          # 安全示例包，不含私有资料
  tests/{unit/,integration/,fixtures/}
```

`team_platform/` 是单一逻辑模块/可部署应用，不是每个目录一个服务。RAG 是首版唯一外部服务。前端开发时由 Vite 代理本地 API，部署时可由平台 API 同源托管。根目录只在批准的集成阶段增加必要配置和用户入口。

### 模块接口与契约

- `RolePackageCatalog.import_archive(bytes) -> ImportResult`：校验、规范化、保存不可变包版本；不执行包中内容。
- `TeamService.create/update(snapshot) -> TeamDefinition`：只接受同项目已有 RoleInstance ID，不授予权限。
- `PermissionPolicy.authorize(actor, project, member, tool_id, args) -> Decision`：每次工具调用前由后端强制检查；角色包的工具声明仅是需求。
- `Planner.create_plan(Goal, TeamSnapshot, Limits) -> PlanDraft`：只输出 schema 化计划，不直接调用工具。
- `LocalRoleExecutor.execute(TaskEnvelope) -> TaskOutcome`：首版本地执行；接口可表达未来远程执行器，但首版只实现本地。
- `ToolRegistry.invoke(ToolInvocation) -> ToolResult`：固定工具 ID、参数/结果 schema、超时、错误类别、调用 ID、幂等标签；授权失败不得进入 connector。
- `KnowledgeConnector.search/get_context(...) -> EvidenceSet`：只经 REST；保留 request ID、generation、citation 和 trace 可用性。
- `RunRepository.append_event(expected_version, event)`：事务化序号与状态检查；模型不能直接写库或改变状态。

核心契约带 `schema_version`。PlanTask、ToolInvocation/ToolResult、ArtifactManifest、RunEvent 用 Pydantic v2 验证。模型 JSON 经解析、schema、授权及预算检查后才可执行。错误至少区分 `invalid_input`、`not_authorized`、`conflict`、`busy`、`timeout`、`tool_failed`、`partial`；不得把异常折叠为空结果。

### 建议 REST 面

- `GET/POST /api/v1/role-packages`、`POST .../import`、按版本 export：目录、预览、导入/导出与兼容性报告。
- `GET/POST /api/v1/projects/{project_id}/role-instances`、`.../teams`：创建项目角色实例和团队 revision。
- `POST /api/v1/runs`：提交目标、team revision、limits 和 idempotency key；服务端固化完整快照。
- `GET /api/v1/runs/{id}`、`/events?after_seq=N`、`/tasks`、`/artifacts`：读取状态、时间线与交付物索引。
- `POST /api/v1/runs/{id}/controls`：经授权执行 pause/resume/cancel/retry/approve_plan。
- Artifact 正文单独授权下载；其他响应优先只返回 ID、hash、metadata。首版是内部产品 API，不宣称公共稳定接口。

## 3. 数据实体及关系

每个项目/运行拥有者都由认证上下文确定，不能信任模型输入。数据库建议独立 SQLite 文件、`PRAGMA user_version` 迁移、WAL、外键和事务；大文件不放 SQLite，存于 Git 忽略的 `storage/team-platform/artifacts/` 内容寻址目录。

| 实体 | 关键字段/关联 | 不变量 |
|---|---|---|
| RolePackage | `package_id`、来源、当前版本指针 | 目录项，不含项目授权、密钥或私有项目文件。 |
| RolePackageVersion | SemVer、schema version、archive/content SHA-256、文件清单、manifest、校验结果 | 内容不可变；同 ID+版本出现不同 hash 时拒绝覆盖。 |
| RoleInstance | project ID、固定 package version/hash、模型 profile ref、context scope ref | 包定义与实例配置分离；权限独立存储。 |
| TeamDefinition/TeamRevision | project ID、成员实例 ID、职责/路由、limits、revision/hash | 更新产生新 revision；成员同项目，版本固定。 |
| PermissionGrant | project/team/member、tool ID、资源范围、到期/撤销状态、授予者 | 缺省拒绝；package/team 声明不等于授权。 |
| CredentialRef | connector ID、secret backend reference、scope/更新时间 | 只存引用，不存 secret；不进入包、模型或普通日志。 |
| TeamRun | owner/project、goal/input refs、team revision、immutable snapshot/hash、limits、状态 | 执行中不读取 TeamDefinition 新版本替换快照。 |
| RunTask | run、负责人、depends_on、input refs、allowed tools、完成条件、deadline/budget、attempt、状态 | 负责人必须在快照中；依赖图无环且任务数有上限。 |
| RunEvent | run、连续 seq、task/member、type/version、safe payload、timestamp、可选 prev hash | 追加式；不存完整 CoT、Authorization 或 provider 原始错误。hash 仅防意外修改，不宣称抗管理员篡改。 |
| ToolCall | run/task/member、call ID、tool ID、参数摘要/hash、grant decision、状态、耗时、幂等键、result ref、error category | 记录 allow/deny；参数原文按敏感度最小化；empty 与 failed 分离。 |
| EvidenceRef | run/task、RAG request、KB、generation/config revision、citation/chunk/document/page、trace status | 可追来源，不宣称 citation 已证明语义蕴含。 |
| Artifact | ID、run/task、kind、media type、size/hash、storage key、schema version、来源 refs、retention 状态 | 写入时校验路径/大小/schema；不可静默替换，变更产生新版本。 |

关系：一个 package 有多个不可变 version；RoleInstance 引用一个精确 version；TeamRevision 引用同项目多个 RoleInstance；TeamRun 引用不可变 TeamRevision snapshot；Run 下有 Tasks、Events、ToolCalls、Artifacts；PermissionGrant 独立授权实例访问特定工具/资源；EvidenceRef 关联来源。不要混表 Team Definition 与 Run，也不要以事件表代替当前状态快照。

## 4. 角色包格式及导入导出

首版建议 ZIP + JSON manifest，版本格式 `agent-role-package/v1`，避免不安全/多义 YAML 解析：

```json
{
  "schema_version": "agent-role-package/v1",
  "package_id": "example.repo-reviewer",
  "version": "1.0.0",
  "name": "Repository Reviewer",
  "description": "Read-only repository analysis role",
  "instructions": "instructions.md",
  "input_schema": "schemas/input.schema.json",
  "output_schema": "schemas/output.schema.json",
  "requested_tools": [{"id": "project.list_files", "reason": "Inspect allowlisted files"}],
  "resources": [{"path": "references/review-policy.md", "sha256": "..."}],
  "compatibility": {"platform_api": ">=1.0,<2.0"},
  "license": "MIT"
}
```

允许 `manifest.json`、UTF-8 `instructions.md`、可选 JSON Schema 和 `resources/` 下声明的静态文件；清单逐项含规范相对路径与 SHA-256。版本用 SemVer；升级产生新记录。`requested_tools`、capability、模型建议仅供预览，不是授权。导出只含包定义，不含 RoleInstance/team/grant/凭据引用/运行记录/用户输入/RAG 语料/产物。

导入先检查 ZIP 中央目录，再安全读取到受限临时区：拒绝绝对路径、`..`、盘符/UNC、反斜线绕过、重复或大小写冲突路径、符号链接、加密条目、超深目录、超文件数、超压缩比/总解压量和不允许类型；禁止脚本执行与依赖安装。全部校验通过才原子保存内容寻址对象，失败不得留半成品。建议默认上限：压缩包 10 MiB、解压 50 MiB、100 文件、单文件 10 MiB、路径深度 6；上线前由产品确认。

导入文本均视作不可信。运行时分层组装平台策略、role instructions、用户目标、项目/RAG 内容；工具授权、schema、资源沙箱由代码强制，不依赖 prompt。角色包格式/安全/兼容性检查不等于作者身份或领域专业认证。

## 5. 运行时、编排与失败语义

### 有界协调策略

- 推荐**有界动态规划 + DAG 执行**，不采用无限自由互聊，也不把静态 DAG 固定到无法响应反馈。Coordinator 产生 `PlanDraft`；后端验证成员、任务数、依赖无环、完成条件、工具集合和预算，生成计划预览；用户确认目标、资料/模型数据范围与 limits 后执行。
- Worker 从 DAG ready queue 派发任务。成员返回结构化 outcome/artifact/error；Coordinator 基于结果决定完成、追加有限 follow-up、生成有版本的新 plan 或请求用户处理。旧任务不静默改写。
- 初始硬上限建议每 run 8 tasks、最大委派深度 2、replan 最多 2 轮、每 task 自动重试最多 1 次、全局并发 1（通过验收才评估 2）；另设每 task 的模型请求/token 上限、run wall-clock deadline 和工具预算。绝对值须在演示复杂度和费用策略确认后定稿；模型不能扩大上限。
- 超任务数/轮次/期限/模型预算时转 `waiting_user` 或 `partial`，不得隐式继续。

### 状态机

Run：`queued -> running -> waiting_user | paused | completed | partial | failed | cancelled`。`waiting_user` 经批准/补输入回 `running`；`paused` 由授权用户恢复。终态 retry 创建新 attempt/run lineage。重启发现活动中不确定操作时标 `interrupted`/`needs_attention`，不宣称精确恢复 in-flight LLM 调用。

Task：`pending -> ready -> running -> succeeded | failed | waiting_user | cancelled | skipped`。重试用新 attempt 和关联事件，不覆盖旧失败。所有 required task 成功才 `completed`；optional 失败但核心产物存在为 `partial` 并列未决项；required 失败且不能安全调整为 `failed`。空查询只能是 `empty` outcome，不替代工具异常或拒绝。

工具/模型至少区分 `ok`、`empty`、`partial`、`timeout`、`rate_limited`、`not_authorized`、`not_published`、`index_damaged`、`invalid_request`、`unavailable`、`tool_error`、`outcome_unknown`。只对瞬态且明确幂等请求做有界重试；权限、参数、索引损坏/未发布不自动重试。调用超时但无法确认 provider 是否完成，记 `outcome_unknown`，不自动重复计费。

pause/cancel 在任务/工具边界检查；对正在运行的 provider 请求写 `pause_requested`/`cancel_requested`，等返回或 timeout 后阻止下一次派发，不谎称已强制停止。首版仅只读操作；副作用工具未来需独立的幂等、确认及审计策略。

运行记录保存 run snapshot、包版本/hash、team revision/hash、model/prompt/config 标识、plan revisions、task 状态、工具授权/结果分类、RAG request/generation/citation/trace 可用性、耗时/用量、终态和 Artifact refs。记录足以重建状态，不保存完整 CoT。用户输入/Artifact 按项目权限、大小上限、保留期限和删除策略管理；hash 不等于匿名化。

## 6. 工具、RAG、凭据与安全

- 首发工具仅 `project.list_files`、`project.read_file`（显式 project root，限文件数/大小/类型）及 RAG search/context。没有 shell、任意 URL、网络爬虫、写文件、Git 操作、部署、发信或工单写入。
- 文件 connector 每次 canonicalize 路径，拒绝根目录外路径、符号链接逃逸、`.env`、凭据、`.git`、`storage/`、缓存和运行结果；敏感文件策略/allowlist 由用户确认。模型拿 opaque resource ID，不传任意路径。
- RAG connector 用 HTTPX 调 `POST /api/v1/search` 且请求 `include_trace=true`；只发送用户配置且后端允许的 KB IDs，不接受模型改变知识范围。保留 request ID、generation/config revision、citation/page、trace status 和失败分类。长上下文优先核验现有 document/chunk/context REST 分页路由；只有公开 API 确实缺功能才提 RAG 最小兼容任务。可借鉴 `RAGClient` 行为，但新平台不导入 `app.client` 或 RAG 内部包。
- MCP 是工具/数据适配协议；平台内首版使用 typed HTTP connector，之后可选接外部 MCP，但仍经同一 PermissionPolicy/ToolRegistry。MCP 不得绕过平台授权。
- API 默认 loopback；配置 Host/Origin allowlist、认证、防 CSRF 和请求体上限。本地 UI 也不等于任意页面可信。跨主机/云部署不属首版，需 TLS、身份、租户与审计专项设计。
- Provider 凭据放环境变量/OS 安全存储或后续 secret backend；数据库只存 CredentialRef。日志、错误、前端不得暴露 Authorization、API key 或原始 provider 请求。UI token 留内存，不放 localStorage。
- 每次调用均由代码验证工具 allowlist、参数 schema、member/project grant、资源范围、超时/预算与调用 ID。未授权调用写 `denied` 事件，不进 connector。
- role instructions、RAG 与项目文件均是潜在 prompt injection 来源。隔离提示是纵深防御，真正边界是后端 grant、固定资源 scope 和无副作用工具。
- 默认仅保留结构化事件、hash/脱敏摘要；完整输入/输出须按用户选择保留，并做访问控制、期限和删除。敏感内容不进入包导出、benchmark、日志或埋点。

## 7. 前端工作台与端到端演示

新建独立 React 19 + TypeScript + Vite 工作台；不把 RAG 管理台改名或复制成团队控制台，可借鉴其 React/FastAPI 同源 API 经验。首屏是实际操作，不是营销页：

1. **项目/运行首页**：项目选择、最近 run、状态过滤、活动/失败/部分完成标记。
2. **角色库**：导入 ZIP；预览 package/version/hash/requested tools/兼容性/警告；查看、锁版本、导出/删除；明确“格式已校验，不代表专业认证”。
3. **角色实例**：选择项目、精确包版本、模型 profile、资料范围、授权工具；Requested 与 Granted 工具分开显示，缺省无权限。
4. **团队编辑器**：添加 coordinator 和成员，设置职责/任务边界/预算并验证后保存 revision。
5. **新建 Run**：填写目标、Team revision、资料范围、模型数据披露和预算；显示计划草案，确认后启动。
6. **运行监察台**：展示总体状态/预算/耗时及 plan revision、task assignee/状态、工具 allow/deny、反馈、replan、错误/重试和产物。通过 `events?after_seq=` 轮询；首版不为“实时”先加 SSE/WebSocket。
7. **Task/Artifact 详情**：输入引用、完成条件、结果/文件、引用来源与 generation、假设/未决项、校验；失败分类可见。
8. **Run 控制**：pause/resume/cancel/retry 按状态授权；cancel 显示请求停止，Worker 确认停止后才终态；不可用动作说明原因。

### 首次演示脚本

- 导入仓库安全示例 `repo-reviewer` 包，查看校验报告，创建项目角色实例并只授权 `project.list_files`、`project.read_file`；Team 为系统 coordinator + 自定义角色。
- 对范围明确的真实但安全项目目标运行（如“依据指定 README、pyproject、测试入口形成测试覆盖/运行风险清单，不改文件”）。启动前展示将发给哪个 provider 的目标/项目数据和预算。
- Coordinator 形成最多 8 个 task 的计划；成员读取白名单文件，根据 tool outcome 继续、调整或说明受阻；交付结构化产物，列出来源/假设/未决项；如用 RAG，展示 request/generation/citation。
- 第二次运行使用确定性 `not_authorized` 或 timeout fixture，必须显示错误事件并停止、改计划或请求用户；状态只能 `failed`/`partial`，不能伪装为“无结果”或 completed。
- Fixture 模式用于可重复 CI；可选 live 模型演示须用户配置并明确批准模型、数据披露和预算。Fixture 证明控制流，单次 live 成功不证明专业能力。

## 8. 技术选型与取舍

| 领域 | 推荐 | 备选/取舍 |
|---|---|---|
| 服务/API | FastAPI + Pydantic 2 + HTTPX，沿用 Python 3.11 仓库栈 | 不引入第二 Web 框架；平台拥有独立 app factory，不从 `RAG/app` 装配服务。 |
| 持久化 | 标准库 SQLite + 自有 migrations + 本地 Artifact 文件目录；单 Worker 起步 | 可借鉴 RAG 的事务/WAL/job 模式，不共用 DB。多主机/多人负载明确前不加 Postgres、Redis 或队列。 |
| 编排 | 代码拥有状态机、schema 验证 DAG、显式协调反馈轮次 | LangGraph 可在未来 checkpoint/分支复杂时对比；首版增加它会引入第二套恢复语义。CrewAI/AutoGen 的自由自主循环不适合当前硬预算/授权/追踪要求。 |
| 模型适配 | 平台自有 `ModelProvider` protocol，薄适配 OpenAI-compatible API，结构化输出与调用/token/time ceilings | 不从 `app.models.llm.*` 导入，避免 RAG 拥有模型 SDK 造成架构倒置。供应商中立仍需显式价格和隐私审查。 |
| 执行后端 | `Executor` protocol 可表达 local/remote；MVP 只启用 LocalExecutor | 不实现 A2A；不把 MCP 当 Agent 委派协议。未来远程身份/能力信任/端点安全另立决策。 |
| 前端 | React 19 + TS + Vite 独立 workspace，REST + polling | 不复制 RAG 源码；暂不加状态管理、router 或实时传输依赖。 |
| 分发 | 复用现有虚拟环境，拟提供独立 `team-platform` module/entrypoint | 当前 root distribution 名为 `rag-knowledge-service`，包发现也不含 `team_platform`。发行策略需在 P6 审查；先保持安装兼容，不悄然重命名。 |

## 9. 分阶段实施与验收

下表是建议执行分解，不是已创建/分发的任务。每阶段须批准后进入；执行者用各自 worktree，跨边界 API 先冻结。

| ID/阶段 | 负责角色与允许写入路径 | 交付物/验收条件 | 定向验证 | 停止条件 |
|---|---|---|---|---|
| P0 基线与契约批准 | Architect/协调；仅轮次文档 | 确认旧轮次处置、新基线/隔离 worktree、包格式、状态机、首发工具、limits、数据保留；冻结 API/event schemas v1。 | `git status/diff/worktree` 清单审阅；schema review。 | 旧批次未决、基线无法隔离、权限/数据发送/预算不清时，不开始 P1。 |
| P1 骨架与持久层 | 后端；仅 `team_platform/{api,domain,persistence,services,composition.py,__main__.py,tests}` | app factory、loopback/auth 边界、独立 SQLite/migrations、health、基础仓储和事件接口。临时 DB 可初始化/升级，事件 seq 事务一致，RAG 无回归。 | migration roundtrip；API auth/Host/Origin/body cap；并发 event append；依赖/import 边界；RAG/Agent targeted smoke。 | DB 共享 RAG 数据、跨界 import、认证默认开放或状态事务不一致。 |
| P2 包/角色/团队 | 后端；仅 `team_platform/domain/{packages,roles,teams}`、其 persistence/services/routes/tests 和 `examples/` | manifest v1、受限 ZIP 导入/导出、hash 固定版本、项目角色实例、TeamRevision；requested tools 不自动 grant。 | 正常 roundtrip；zip slip/bomb/文件数/大小写冲突/symlink/缺文件/hash/schema/SemVer 冲突用例；导出 secret scan。 | 不能原子导入、旧版本可覆盖、包声明自动获得权限。 |
| P3 权限与只读连接器 | 后端；仅 `team_platform/{connectors,domain/permissions,services,tests}`；RAG 改动另提最小兼容任务 | 固定 tool registry、project list/read sandbox、RAG REST search/context connector、调用 ID/timeout/error、授权与 EvidenceRef。无授权不触达工具；KB scope 不由模型决定；空与失败分离。 | HTTPX mock contract；越权 KB/project；路径 traversal/symlink/敏感文件；timeout/403/not_published/empty；日志 secret scan；无 RAG private import。 | 需要直连 RAG DB、shell/任意 URL 才能演示，或失败变成 empty。 |
| P4 有界运行时/Worker | 后端；仅 `team_platform/{orchestration,runtime,domain/runs,services,persistence,tests}` | 结构化 PlanDraft、DAG 检查、run/team/package snapshot、持久任务队列/单 Worker、模型 adapter、feedback/replan limits、状态控制和 Artifact。Coordinator + 一个本地角色完成 happy path；所有上限服务端执行；重启语义明确。 | fake model/connectors 覆盖成功、empty、timeout、403、非法参数、重复调用、预算耗尽、pause/cancel、worker restart、幂等 retry、required/optional partial、model timeout `outcome_unknown`。 | 状态不可重建、重复调用超预算、授权绕过、cancel 谎报已停止。 |
| P5 工作台与端到端演示 | 前端写 `team_platform/frontend/`；后端只补冻结 API；集成 AI 只改批准的 packaging/docs/root entry；跨界测试在根 `tests/` | 实现角色/团队配置、Run 启动确认、事件监察台、产物/引用/失败视图；带安全示例包与确定性失败 fixture。完成决策中的导入→实例→团队→有限计划→工具→反馈/调整→产物闭环；失败不可伪装成功。 | `npm ci && npm run build`；临时 SQLite + fake providers E2E；桌面/窄屏验收；手工按演示脚本；检查 storage 产物不入库。 | 需真实凭据才能跑主链、失败不可读、lockfile/build 不可复现或需改旧启动行为。 |
| P6 安全/兼容/运行手册 | 集成/安全复核；仅批准的 `team_platform/`、根 README/pyproject/入口、根 `tests/` | 审查 retention、备份、package upgrade、旧 CLI/RAG 兼容、安装/停止说明；RAG 故障不拖垮平台，平台故障不拖垮 RAG。 | platform 全测试；`RAG/tests`、`agent/tests` 回归；benchmark offline tests（不跑 live）；跨边界 smoke；secret/dependency/build checks。 | 越权、路径逃逸、密钥泄漏、状态不一致或旧入口回归，停止发布返工。 |

每阶段汇报改动路径、schema/API 变化、命令与结果；遇到越界文件先停止并提方案，不以“共享依赖”自动扩大授权。失败阶段保留日志/测试证据，不清理用户数据或覆盖旧状态，不开始后续阶段。

## 10. 测试与产品验收边界

验收产品机制，使用 deterministic fake providers/fixtures，避免模型波动掩盖状态控制：

1. **Package**：正常导入/预览/版本锁定/导出；zip slip、zip bomb、畸形 schema/hash 被拒；证明没有脚本执行。
2. **Team/权限**：Requested tools 与真实 grant 分开展示；无 grant 时记录拒绝且 connector 未调用；跨 project/member/resource/KB 均拒绝。
3. **Plan/运行**：schema 与 DAG 合法；未知成员、超上限、环或缺完成条件不可启动；Run 固化 package/team revision 和 hash。
4. **反馈闭环**：fake tool 首次返回可操作结果，成员第二步读取结果后调整任务/产物；事件有序并展示原因摘要，不展示 CoT。
5. **失败语义**：timeout/403/not_published 和 `empty` 分别显示；required 失败不得 `completed`；optional 失败只能 `partial` 并列限制。
6. **追踪**：run/task/event/call/artifact 可关联；RAG citation/generation/request ID 缺失时标记 unavailable；snapshot 锁定包/team revision。
7. **隐私**：包导出、事件、错误与日志扫描密钥/Authorization/provider 原文和不必要的完整提示；数据保留与删除行为有测试。
8. **可用性**：演示者可以创建角色/团队、启动 run、查看失败、打开 artifact；桌面和窄屏状态/操作不重叠。

这些测试只证明样例上的产品路径与安全约束。角色是否擅长代码审查、威胁建模或任一专业领域不属于产品验收；不建立角色排行榜、专家认证分数或专业能力 benchmark。若以后需评估专业度，须另立决策并定义代表性数据、数据授权与专家评审方案，与格式安全和功能测试分开。

## 11. 最大风险、依赖和待决问题

### 最高风险

1. **旧批次/基线冲突**：dirty worktree 混有三模块差异，旧验收材料不完整。未先归档就开新方向，可能遗失或误带数据/代码。P0 是硬门禁。
2. **工具权限由 prompt 取代**：包声明、模型计划和 MCP 描述都不是 grant；每次调用若无后端强制校验就可能越权。
3. **持久运行与重复成本/动作**：数据库不能精确恢复 in-flight 请求；错误 retry 会重复计费/冲突。未知结果需 `outcome_unknown` 并人工确认。
4. **项目数据外发**：代码/文档可能发送给外部模型；启动前显示 provider、范围和预算，拒绝未经授权资料，不默认扫描/上传全仓库或完整 RAG 上下文。
5. **包供应链与注入**：ZIP 可带恶意指令、超大文件、路径穿越；严格解析、无脚本、无依赖；执行能力由代码控制。
6. **边界耦合**：旧 Agent 直接导入 RAG 模型 client；新平台若依赖 `app.*` 会受 RAG 内部重构影响。新 runtime 只依赖自己的 protocol 和 RAG REST。

### 依赖与 Architect/用户待决

- 旧 `2026-11-14-current-batch` 的 acceptance/dirty changes 如何封存、哪些作为后续基线、由谁确认？协调 AI 不代做此判断。
- 首发是否仅单机单用户/本地 workspace？推荐单机单用户，但仍需本地认证和项目隔离；多人/多租户会改变身份、DB、授权和审计设计。
- 是否允许项目文件/目标发送给外部模型？推荐每次 Run 明示 provider 与数据范围；配置未完成时只允许 fake demo。
- 是否只支持 ZIP 包（推荐），默认文件大小/类型上限多少？目录导入仅可作为开发便利，不能混成分享格式。
- 运行失败/partial、pause/cancel/retry 文案及数据保留期？建议元数据保留、原始输入/完整产物短期可删，期限待确认。
- 模型预算建议以请求数/token/time 作为硬限；货币估算仅在明确价格表时提供，不能以 provider usage 宣称严格账单上限。需确认规则。
- 发行包策略：沿用现有 root distribution 并加入口，或拆独立 distribution？建议先不重命名现有包，P6 单独审查。
- 多用户、云部署、远程角色/A2A、写工具、跨重启无缝续跑均移出 MVP，未来需另行决策。

## 12. 实施顺序与总停止条件

顺序固定为：旧批次/基线决策 -> API/实体/事件契约 -> 平台骨架与独立存储 -> 包/角色/团队配置 -> 权限与连接器 -> 有界运行时/Worker -> 前端闭环 -> 安全与旧产品兼容验收。前端只能在 OpenAPI/事件契约冻结后并行开发。

以下任一出现，暂停并报告阻塞，不扩展范围：基线不清或数据范围未授权；跨项目/KB 越权；包路径逃逸/脚本执行；无硬预算/任务上限；失败被记成 empty/completed；运行/事件/产物不能关联；密钥进入日志/导出；需未批准改变 RAG REST 或旧 CLI；需要微服务/队列但没有负载/故障证据。

**本计划不授权实现。** 只有 Architect 和用户明确批准计划、旧批次处置、基线及本地模型/数据策略后，才更新 `CURRENT.md` 状态并建立隔离实现工作区。在此之前只保留本计划和现有材料。

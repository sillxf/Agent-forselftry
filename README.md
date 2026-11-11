# AI-SecOps-Agent

当前仓库由三个边界组成：

- RAG/：知识库管理与证据检索服务，包含 API、Worker、管理台和 MCP 适配。
- agent/：安全告警调查 Agent，通过 RAG 的 REST 接口获取证据并生成调查报告。
- benchmark/：冻结数据、评测代码和实验入口，不参与服务启动。

## 快速开始

首次安装：

~~~powershell
python -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -e .
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
.\\.venv\\Scripts\\python.exe -m app init
~~~

Windows 下双击根目录的 启动.cmd 会启动 RAG API、Worker 并打开管理台；停止.cmd 会停止它们。

命令行启动：

~~~powershell
.\\.venv\\Scripts\\python.exe -m app serve --port 8090
.\\.venv\\Scripts\\python.exe -m app worker
~~~

管理台地址：

~~~text
http://127.0.0.1:8090/
~~~

## 目录

~~~text
RAG/app/          RAG 服务 Python 包
RAG/frontend/     管理台源码
RAG/mcp_server/   MCP 适配层
RAG/tests/        RAG 确定性测试
RAG/scripts/      桌面启动和辅助脚本
RAG/migrations/   本地运行数据的备份、恢复和迁移
agent/            调查 Agent 代码和测试
benchmark/        冻结数据、评测和实验
tests/            跨边界 smoke 检查
storage/          本机运行数据，Git 忽略
~~~

app 是安装后的 Python 包名，源码实际位于 RAG/app/。Agent 只通过 RAG API 工作，不直接读取 RAG 的数据库、原件或索引。

## 常用检查

~~~powershell
.\\.venv\\Scripts\\python.exe -m unittest discover -s RAG/tests -p "test_*.py"
.\\.venv\\Scripts\\python.exe -m unittest discover -s agent/tests -p "test_*.py"
.\\.venv\\Scripts\\python.exe -m unittest discover -s benchmark/tests -p "test_*.py"
.\\.venv\\Scripts\\python.exe -m tests.smoke
~~~

更具体的入口和当前限制分别见 RAG/README.md、agent/README.md 和 benchmark/README.md。运行数据放在 storage/ 与 benchmark/runs/，不提交 Git。

# 辅助入口

- `export_product.py`：源码导出，不含历史、运行数据和凭据。
- `desktop.ps1`：根目录“启动.cmd / 停止.cmd”的 Windows 启停入口，不复制业务管理逻辑。

日常业务管理统一使用管理台、REST API 或 rag-service CLI。

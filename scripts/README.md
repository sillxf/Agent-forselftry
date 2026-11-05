# 辅助入口

- `export_product.py`：源码导出，不含历史、运行数据、评测结果和凭据。
- `load_test.py`：对运行中的服务做有界压测，输出延迟分位数、吞吐和状态码分布。
- `desktop.ps1`：根目录“启动.cmd / 停止.cmd”的 Windows 启停入口，不复制业务管理逻辑。

日常业务管理统一使用管理台、REST API 或 rag-service CLI。

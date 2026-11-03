# 离线数据维护

`service_data.py` 提供现有数据迁移、备份、恢复、校验及跨路径恢复，供 CLI 显式调用。代码目录整理本身不修改数据库 schema，不重建已有索引。

使用 `rag-service --data <目录> backup <新备份目录>`；恢复使用 `rag-service restore <备份目录> <新数据目录>`。执行前停止 API 和 Worker，操作会检查文件锁。旧格式迁移使用 `migrate-legacy --help`，要求备份目录和明确停止写入确认。

不得把凭据、实际知识库、模型或迁移生成结果提交到此目录。

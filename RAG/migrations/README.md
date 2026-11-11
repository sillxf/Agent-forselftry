# 本地数据维护

service_data.py 提供运行数据的备份、恢复、校验和旧格式迁移。执行备份、恢复或迁移前先停止 API 和 Worker；生成的备份、凭据和实际知识库不提交 Git。

~~~powershell
rag-service --data <数据目录> backup <备份目录>
rag-service restore <备份目录> <新数据目录>
migrate-legacy --help
~~~

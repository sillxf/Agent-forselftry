# 接入方式

服务只返回证据，不生成答案。下面三种接入方式都使用管理台“访问与审计”里创建的只读 Key，Key 只能访问创建时选定的知识库。知识库 ID 在管理台总览里可以看到，也可以通过 `GET /api/v1/knowledge-bases` 查询。

## Dify（外部知识库）

本服务实现了 Dify 的 [External Knowledge API](https://docs.dify.ai/en/cloud/use-dify/knowledge/external-knowledge-api)。

1. 在 Dify 的“知识库 → 外部知识库 API”中新增一项。API Endpoint 填 `http://<主机>:8090/api/v1/dify`（Dify 会自动在后面加 `/retrieval`），API Key 填本服务的只读 Key。
2. “连接外部知识库”时，External Knowledge ID 填本服务的知识库 ID。
3. Dify 的 Top K 和 Score 阈值会原样传过来。阈值作用在每条结果的 `relevance` 上：开了重排就是重排分数，否则是与问题的余弦相似度。这两种分数的尺度不同，阈值建议先设 0，按检索测试的实际结果再调。

Dify 运行在 Docker 里而本服务在宿主机时，要把宿主机地址加进 `RAG_ALLOWED_HOSTS`（例如 `host.docker.internal`），否则请求会因 Host 校验返回 403。

元数据过滤（`metadata_condition`）支持 is、is not、contains、in、not in、大于、小于、before、after、empty、not empty。字段名 `document_id`、`file_type`、`source` 对应文档本身的属性，其他字段名对应文档元数据里的键。

## MCP 客户端（Claude Desktop、Cursor、Cline 等）

本地客户端用 stdio 方式最简单。客户端启动 `rag-service mcp-stdio`，这个进程再通过 REST 访问正在运行的服务：

~~~json
{
  "mcpServers": {
    "knowledge": {
      "command": "D:\\AI-SecOps-Agent\\.venv\\Scripts\\rag-service.exe",
      "args": ["mcp-stdio"],
      "env": {
        "RAG_SERVICE_URL": "http://127.0.0.1:8090",
        "RAG_SERVICE_TOKEN": "<只读 Key>",
        "RAG_SERVICE_KNOWLEDGE_BASES": "<知识库 ID>"
      }
    }
  }
}
~~~

支持 Streamable HTTP 的客户端也可以直接连 `http://<主机>:8090/mcp/`，请求头带 `Authorization: Bearer <只读 Key>`。

提供 7 个只读工具：

| 工具 | 用途 |
| --- | --- |
| `rag_list_knowledge_bases` | 列出 Key 能访问的知识库和它们的描述 |
| `rag_search` | 检索。可附带最多 4 条改写查询（例如英文翻译）、过滤条件和 `min_score` |
| `rag_get_context` | 读取命中片段前后的相邻片段或相邻段落 |
| `rag_get_chunk` | 读取单个片段 |
| `rag_get_document` | 分页读取文档已发布的内容 |
| `rag_get_document_outline` | 读取文档目录，用于长文档导航 |
| `rag_list_documents` | 列出文档 |

给调用方模型的建议：中文问题查英文资料时，在 `queries` 里补一条英文翻译。冻结基准上这一项把 MRR@5 从 74 提高到 89。命中片段被截断时，用 `rag_get_context` 读前后文，不必读整篇文档。

## REST

~~~bash
curl -s http://127.0.0.1:8090/api/v1/search \
  -H "Authorization: Bearer <只读 Key>" -H "Content-Type: application/json" \
  -d '{
    "query": "密码喷洒为什么能绕过账户锁定",
    "queries": ["password spraying account lockout"],
    "knowledge_base_ids": ["<知识库 ID>"],
    "top_k": 5,
    "filters": {"metadata.year": {"$gte": "2024"}},
    "min_score": 0.3
  }'
~~~

每条结果包含原文 `content`（默认是整个所在段落，超出上下文预算时退回命中片段）、命中片段 `chunk_content`、`relevance` 和 `relevance_source`、来源 `source`、章节 `section_path`、页码，以及可以直接用来引用的 `citation`。`include_trace: true` 会额外返回各路召回的候选和耗时。

过滤条件支持完全相等、列表（任一匹配），以及运算符 `$eq $ne $in $nin $gt $gte $lt $lte $contains $exists`，可以用 `$and` / `$or` 组合，最多嵌套 3 层、20 个条件。两边都是数字时按数值比较，否则按文本比较，所以 `2024-05-01` 这样的 ISO 日期能正确排序。可用字段有 `document_id`、`file_type`、`source`（文件名）和 `metadata.<键>`。

读取前后文：

~~~bash
curl -s "http://127.0.0.1:8090/api/v1/knowledge-bases/<知识库 ID>/chunks/<chunk_id>/context?before=2&after=2&unit=child" \
  -H "Authorization: Bearer <只读 Key>"
~~~

`unit=parent` 返回相邻的段落。`before` 和 `after` 取 0 到 5，返回的每一项都带 `offset`，命中的那一项为 0。

错误码：请求参数有误返回 422（`code=invalid_request`）；知识库还没有发布版本返回 409（`code=not_published`）；索引校验失败返回 503（`code=index_integrity`）；Key 的每分钟配额用完返回 429。完整的运维说明见 [operations.md](operations.md)。

Python 调用方可以直接使用 `app.client.RAGClient`。它只依赖 httpx，不会加载模型或解析器。

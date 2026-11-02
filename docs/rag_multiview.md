# 可选 Question Multi-View 检索

本次只增加一种辅助表示：每个适用的原始 Child，最多生成一条中文问题、一条英文问题。
默认检索依然是 BGE-M3 + Dense/BM25/RRF。这里的 Multi-View 不是 BGE 原生 ColBERT 多向量模式。

**状态：实验性可选实现，未向当前生产索引发布。** 首轮 100 题中，全部可答题 Parent Recall@5
从 94.44% 降到 84.44%，中文→英文从 92.31% 降到 74.36%；不建议把它当成检索升级默认启用。
工具接口可用不等于效果已经通过验收。生产仍只有原来的 3 份 Markdown，不会自动导入评测的 21 份文档。

## 边界

- View 是检索表达，不是知识证据；最终正文、Chunk/Parent ID、文档和页码全部取自原文。
- View 独立建库，不追加到原文 `store.records`，不进入原文 BM25 或 Ground Truth。
- 生成是显式离线操作；启动、加载和查询不调用生成 LLM。
- 生成仅接收原始 Chunk，不接收 Benchmark 问题、答案或 Evidence 标签。
- LLM 输出使用批次内整数索引，本地映射到原始 Child ID；不让模型创建文档身份。
- 标题、空内容等不适合生成问题的 Chunk 可以跳过，数量写入生成 manifest。生成问题未经人工认证。
- 每个 Child 每种语言最多一条 View；校验原文 hash 和 Parent 映射，避免旧 View 绑定新内容。
- 视图生成 LLM/Prompt 版本写入记录，固定产物可重复编码，无须再次调用生成 LLM。

## 实际查询流程

```text
Query → 编码一次 ┬→ 原始 Dense（候选预算不变）──────────┐
                └→ Question View Dense → 原始 Child 去重 ├→ 内层 RRF60
原始 Query → 原有 BM25 ────────────────────────────────┴→ 外层 RRF60
                                                         ↓
                                               原有 ParentContextBuilder
                                                         ↓
                                                原文正文及引用来源
```

View 候选按第一次出现即最佳排名聚合；一个 Child 在辅助通道最多获得一次投票。
辅助库最多取 `2 × 原 Dense 候选预算`，去重后保留原候选预算数量。
无新增权重、路由分类器、充分性判断、自动重试、Reranker 或通用插件框架。
保留原文检索通道不意味着 Top-K 不会退步，必须同时观察改善与退步。

## 离线生成并发布到生产索引

先有正常的原文索引。以下 PowerShell 命令在仓库根目录执行：

```powershell
# 尚未建原文索引时才需要运行这一行。
python -c "from app.rag.retriever import KnowledgeRetriever; KnowledgeRetriever()"

$pointer = Get-Content app/storage/indexes/current.json -Raw | ConvertFrom-Json
$chunks = "app/storage/indexes/$($pointer.generation)/chunks.jsonl"
python scripts/rag_question_views.py generate --chunks $chunks --output app/storage/question_views.jsonl
python scripts/rag_question_views.py build --views app/storage/question_views.jsonl
```

生成使用现有 `.env` 的 LLM 配置；`--batch-size` 默认 8、`--workers` 默认 1。
输出文件禁止覆盖，失败会保留 `completed: false`，不能拿它当完整生成结果发布。
生成模型可能遗漏有用内容或提出不准确的问题；结构校验不是事实审核。

构建只编码 View，复用当前原文向量、Chunk 和元数据；不重新解析文件。
原文模型和配置必须与当前 Generation 匹配。原文变动时先重建原文索引，再重新生成视图；
普通 `build_index()` 不隐式生成或继承旧 View。

Generation 新增可选的 `views/` 目录，包含 FAISS、View 记录和模型 manifest。
不升级旧索引格式版本：旧 Generation 无需迁移，继续使用 Hybrid。
保存新 Generation → 准备完整查询组件 → 发布 current.json → 切换内存引用。
发布前失败不影响旧版本，也不删除旧 Generation。其他服务进程需要重启才能加载新指针。

## API 与 LLM Tool

```text
GET /knowledge/search?q=如何阻止受感染主机继续对外通信&k=3&retrieval_mode=multi_view
```

不传 `retrieval_mode` 时行为与之前相同，默认 `hybrid`。
若当前 Generation 没有辅助索引，显式请求 `multi_view` 返回 HTTP 409；不会悄悄换成 Hybrid。
未知模式由接口校验返回 422。

Agent 增加 `knowledge_search(query, retrieval_mode="hybrid", top_k=5)` 工具。
可选模式枚举根据当前索引生成：没有辅助库时只向 LLM 提供 `hybrid`。
工具只暴露这三个参数，不暴露融合权重、View 类型和底层阈值。

- `hybrid`：默认；普通问题、精确技术术语、CVE/ATT&CK ID、IP、Hash、命令、路径。
- `multi_view`：口语化、间接表达、术语不明确，或前次查询缺少有效证据。

工具每次只执行指定模式。Agent 可显式再次调用，但没有强制 Hybrid→Multi-View 重试链。
沿用已有 Agent 工具轮数上限。本阶段不声称验证了真实 LLM 的模式选择质量或拒答可靠性。
工具召回的新增 Parent 会并入调查结果的 knowledge，方便查看实际使用的原文证据。
`matched_view_ids`/`matched_view_types` 是诊断元数据，不是引用证据。

## 重放固定 100 题实验

冻结原文来自已有 BGE-M3 B 组；文档元数据沿用相同的 MiniLM 冻结参考，
脚本校验相同 Chunk、原向量 hash、模型权重/tokenizer、数据集和语料 manifest。

```powershell
# 第一次生成。重放已有实验时直接使用交付的冻结 question_views.jsonl，跳过此步骤。
python scripts/rag_question_views.py generate `
  --chunks evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/bge_index/chunks.jsonl `
  --output evaluation_results/local_question_views/question_views.jsonl

python scripts/run_multiview_experiment.py --offline `
  --views evaluation_results/local_question_views/question_views.jsonl `
  --output-dir evaluation_results/local_multiview_run
```

现有结果和输出目录禁止覆盖。输出包括：

- 两组逐题 Top-K、原文、View 命中 ID、分语言/题型/难度指标及失败报告；
- `comparison.md`、`changes.json`：改善与退步，含排序变化；
- `status.json`：历史 Hybrid 排名指纹一致性与查询错误数；
- 固定生成问题、manifest、模型和代码指纹、源码快照、新的独立索引 Generation。

只评估检索，不运行回答生成或人工审核。不可答题不计入普通 Recall/MRR。
第一轮固定结果见 `evaluation_results/baselines/2026-11-02_security_v1_question_multiview/`。

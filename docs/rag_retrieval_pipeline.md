# 查询管线组件化

本轮仅拆分已有查询能力，不增加算法、模型实验或占位模块。
生产默认仍为 BGE-M3 + Dense/BM25Plus + RRF；API 与索引格式保持不变。

## 组件与职责

| 文件（app/rag/retrieval/） | 组件 | 职责 |
| --- | --- | --- |
| dense.py | DenseRetriever | 注入查询编码函数和已加载 VectorStore，返回向量召回 Child |
| sparse.py | SparseRetriever | 持有同一批 Child records、BM25Plus 和倒排候选；包含现有分词函数 |
| fusion.py | RRFFusion | 多路等权 RRF；按 chunk_id 合并并保留 Dense/Sparse 分数 |
| context.py | ParentContextBuilder | 根据 Child 顺序恢复 Parent、按 parent_id 去重并继续补足 K |
| pipeline.py | RetrievalPipeline | 选择策略、控制候选数量、编排组件并返回现有结果结构 |

```text
Query ── DenseRetriever ─┐
                        ├─ RRFFusion ─ ParentContextBuilder ─ Result
Query ─ SparseRetriever ┘
```

Dense 或 BM25 单路模式绕过 Fusion。候选数量仍是每路 max(配置值, K×4)。
Child Top-K 和 Parent Top-K 分开截取；Parent 去重不能只扫描已截断的 Child Top-K。
融合使用 RRF60，同分依次比较 Sparse 分数、Dense 分数、Chunk ID；Sparse 同分保持语料顺序。
同一 Child 在不同路分别贡献 RRF；单路重复记录不重复投票。

## 独立构造和替换

以下 store 与 parents 是已加载的、相互匹配的向量库与 Parent 映射。
组件不负责读取知识目录、切分或发布索引。

```python
from functools import partial

from app.rag.embedder import embed_texts
from app.rag.retrieval.dense import DenseRetriever
from app.rag.retrieval.sparse import SparseRetriever
from app.rag.retrieval.fusion import RRFFusion
from app.rag.retrieval.context import ParentContextBuilder
from app.rag.retrieval.pipeline import RetrievalPipeline

pipeline = RetrievalPipeline(
    dense=DenseRetriever(store, partial(embed_texts, model_name="BAAI/bge-m3")),
    sparse=SparseRetriever(store.records),
    fusion=RRFFusion(),
    context_builder=ParentContextBuilder(parents),
    dense_top_k=20,
    bm25_top_k=20,
)
rankings = pipeline.search_rankings("中文查询", k=2)
all_candidates = pipeline.rank_candidates("中文查询", k=2, strategy="hybrid")
```

替换任一构造参数即可复用其他组件；不要求共同基类、插件注册或工作流引擎。
Dense/Sparse 组件接口均为 retrieve(query, limit)；Fusion 为 fuse(rankings)；
上下文构建为 build(ranked_candidates, k)。

候选继续使用现有 dict：chunk_id、parent_id、document_id、content、search_text、
source_name、block_ids、页码等字段不变，新增阶段分数不能覆盖其他阶段分数。
Dense/Sparse 的原生分数、融合后的 score 及现有父子来源字段保持原协议。
返回结果不改变已加载的源记录。索引绑定期间不要原地修改 records/parents。

## KnowledgeRetriever 的边界

现有 KnowledgeRetriever 是兼容入口，继续管理解析、切分、索引持久化、Generation、
延迟初始化和锁；search/search_rankings/build_index 的调用方式不变。
查询算法已移出，仅通过 pipeline 调用组件。

- retriever.pipeline：公开访问当前已绑定的 Pipeline，首次访问按原规则加载或构建索引。
- retriever.attach_index(store, documents, parents, model_name=...)：显式绑定完整的内存/冻结索引，
  同时重建 Dense/Sparse/Parent 组件，不写 current.json。主要供冻结实验使用。
- 正常加载、重建也复用同一绑定入口。原 Pipeline 引用保留原快照，不会掺入新 postings/Parent。
- 模型查询编码必须与该向量库一致；attach_index 不负责把一种模型的向量转换成另一种。
- 模型或组件配置应在重新绑定/构造时指定，不靠事后修改 model_name 或 store 自动刷新其他组件。
- 单独构造的 Pipeline 不管理索引重建或生命周期；应用正常请求继续使用带锁的 KnowledgeRetriever。

## 评测边界与兼容

评测通过公开 Pipeline 或组件组合路由，不再调用 Retriever 的私有查询方法，
也不再分别赋值 store/parents 后私自重建 BM25。

B/C 双路实验复用生产 RRFFusion。早期 crosslingual 实验的外层 Query 融合仍保留
其既有策略（首路元数据、仅 ID 打破同分），不替换成生产策略以免改写历史实验语义。
这不是新的生产路由。

本轮没有实现 Reranker、Compressor、EvidenceValidator、语义去重或上下文长度优化。
没有调整 Ground Truth、重跑模型对比、覆盖历史实验或重建生产索引。

## 验证

- 原有 API、分析、Sparse 候选计分、索引持久化和评测测试继续复用。
- 补充三个集中测试：组件替换/Parent Top-K、多路融合/原记录不变、重建后完整快照绑定。
- 本地额外保存并核对 18 组重构前后的真实 BGE 查询输出（3 个 Query × 2 个 K × 3 种策略）：
  排名、分数、上下文及元数据完全相同；FastAPI TestClient 真实路由返回也相同。
- 真实查询对照不是新一轮模型测评；记录在本地 .pytest_cache/component-parity/，不改历史基线。

本轮完整回归：`python -m pytest -q`，126 passed、10 skipped；跳过的是需显式启用的 PDF/OCR 模型测试。

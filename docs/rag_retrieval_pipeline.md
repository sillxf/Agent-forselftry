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

## 独立文档处理（第一步提取）

`app/rag/ingestion/pipeline.py` 新增 `IngestionPipeline`，依次完成文档发现、内容去重、
解析、跨页合并、结构恢复与 Parent/Child 切分。输出 `IngestionResult`，仅含 documents、
parents、children；现有 DocumentRecord、ParentChunk、ChildChunk 模型不变。

Parser 和两个 Chunker 显式传入。Pipeline 自己不创建 Embedding 模型，不调用编码，
不建立 VectorStore，也不写 metadata.db/current.json。Parser 已有的可选解析归档行为保留。
支持的格式与原有文档发现逻辑一致，不限于 PDF。

独立检查切分（模型/Tokenizer 由调用方提供；以下沿用应用有效预算计算）：

```python
from app.config import (
    RAG_EMBEDDING_MODEL, RAG_PARENT_MAX_TOKENS, RAG_CHILD_MAX_TOKENS,
    RAG_CHILD_OVERLAP_TOKENS, RAG_KNOWLEDGE_DIR,
)
from app.rag.embedder import get_model
from app.rag.ingestion.docling_parser import DoclingParser
from app.rag.ingestion.pipeline import IngestionPipeline
from app.rag.chunking.parent_chunker import ParentChunker
from app.rag.chunking.child_chunker import ChildChunker

model = get_model(RAG_EMBEDDING_MODEL)  # 调用方显式取得 tokenizer，不执行向量编码
special = model.tokenizer.num_special_tokens_to_add(pair=False)
budget = min(RAG_CHILD_MAX_TOKENS, model.max_seq_length - special)
ingestion = IngestionPipeline(
    parser=DoclingParser(),
    parent_chunker=ParentChunker(model.tokenizer, RAG_PARENT_MAX_TOKENS),
    child_chunker=ChildChunker(
        model.tokenizer, budget, min(RAG_CHILD_OVERLAP_TOKENS, budget - 1),
    ),
)
result = ingestion.run(RAG_KNOWLEDGE_DIR)  # 也可传入其他 PDF/混合文档目录
print(len(result.documents), len(result.parents), len(result.children))
```

调用方也可传入自己的 Tokenizer/Chunker，不必使用或加载 Embedding 模型。
`KnowledgeRetriever` 仅在实际需要新建索引且有文档时才取得模型 Tokenizer；
`build=False` 和复用已有索引不会因此提前加载模型。显式传入 Tokenizer 的旧行为不变。

Facade 内部通过 run(..., files=files) 复用索引签名已发现的有序文件列表，
避免再次扫描目录造成签名与处理集合偏离；普通独立调用只需传目录。
处理按原有顺序执行并保留相同的内容去重、文件名、Block/Parent/Child ID 和切分预算。

本步只提取 IngestionPipeline：Embedding、VectorStore、SQLite 和索引发布仍在原入口，
尚未提取 IndexingPipeline 或 SnapshotRepository，也未调整发布/绑定顺序。

本步验证：完整回归 129 passed、10 skipped（PDF/OCR 模型测试默认跳过）；另用本地缓存的
Docling 模型实际解析 PDF + Markdown，与提取前保存结果逐字段比较，documents、parents、
children（含 ID）及通过原入口重建后的查询结果完全一致。对照过程使用本地测试 Embedding，
不是新一轮模型效果评测；独立 Ingestion 调用未执行向量编码或创建向量索引。

## 独立索引构建（第二步提取）

`app/rag/indexing/pipeline.py` 新增 `IndexingPipeline`，接收已有的 `IngestionResult`：

```text
IngestionResult(documents / parents / children)
  → Child.search_text 按原顺序编码
  → 创建新的 VectorStore 并添加向量/Child 记录
  → IndexSnapshot(store / documents / parents)
```

`IndexSnapshot` 是简单的内存结果对象，不是已发布的 Generation，也不是不可变快照管理器。
文档和 Parent 使用原结果中的列表；Child 记录按原有 model_dump(mode="json") 协议生成。
使用期间不要原地修改这些元数据。

```python
from functools import partial

from app.config import RAG_EMBEDDING_MODEL
from app.rag.embedder import embed_texts
from app.rag.indexing.pipeline import IndexingPipeline
from app.rag.indexing.vector_store import FaissVectorStore

# result 为前面 ingestion.run(...) 的输出，只需处理文档一次。
indexing = IndexingPipeline(
    embed=partial(embed_texts, model_name=RAG_EMBEDDING_MODEL),
    store_factory=FaissVectorStore,
)
snapshot = indexing.build(result)
print(len(snapshot.store.records), len(snapshot.documents), len(snapshot.parents))

# 之后复用相同 Chunk：替换编码函数或 store_factory，不再调用 Parser/Chunker。
rebuilt = indexing.build(result)  # 创建独立的新向量库，不向旧库追加。
```

要更换 Embedding，只需注入另一个 embed(texts) 可调用对象；要换向量库，传入
store_factory(dimension)。编码输出沿用 float32，归一化及搜索行为仍由原 FaissVectorStore 处理。
新模型必须能够容纳已有 search_text；本管线不重切 Chunk，也不自动处理新模型的截断。
查询编码必须与向量库使用同一模型，不能将新向量绑定到旧查询模型。

可单独装配已有查询管线，不必写磁盘或调用文档处理：

```python
from app.rag.retrieval.pipeline import RetrievalPipeline

query_pipeline = RetrievalPipeline.from_index(
    snapshot.store,
    {parent.parent_id: parent for parent in snapshot.parents},
    embed=indexing.embed,
)
results = query_pipeline.search_rankings("中文问题", k=2)
```

也可使用原兼容入口的 attach_index，显式传入与该向量库匹配的模型/编码配置。
独立 build 不需要文档目录，即使原文档暂时不可访问也可以使用内存中的 Chunk 结果。
没有 Child 时不调用编码函数，继续创建原有的 1 维空索引。

KnowledgeRetriever 现在委托 IngestionPipeline 处理文档、IndexingPipeline 编码建库，
随后仍调用原 _save 和 attach_index。构造参数、search/search_rankings/build_index、
索引格式、检索策略、默认 BGE-M3、Top-K 和 Chunk ID 不变。
本步不迁移 SQLite/current.json，不调整发布/绑定顺序，不抽取 SnapshotRepository，
不增加模型实验、组件协议或新的运行时机制。

本步验证：完整回归 133 passed、10 skipped（需显式启用的 PDF/OCR 模型测试默认跳过）。
复用相同 Chunk 注入两种不同维度的测试编码函数，验证新库独立、记录/ID 不变；
Embedding 或 VectorStore.add 失败时，原内存查询管线和磁盘 current 指针均保留。
另用真实 BGE-M3 对已有 12 个生产 Chunk 做内存重建，禁止 Parser/Ingestion 调用，
新旧向量在 1e-6 容差内一致、生产指针未修改；12 组重构前后的本地测试查询输出完全一致。
这些是行为回归，不是新增模型效果实验，也没有发布新的生产索引。

## 快照仓库与兼容 Facade（第三、四步整理）

`app/rag/indexing/snapshot_repository.py` 提取了原 Retriever 的 SQLite、Generation
保存/加载和 current.json 管理。KnowledgeRetriever 不再实现 SQL 或文件发布：

```text
KnowledgeRetriever（兼容入口、默认装配、延迟初始化、进程内锁）
  ├── IngestionPipeline：解析与切分
  ├── IndexingPipeline：Child 编码和内存向量库
  ├── SnapshotRepository：保存、加载、发布磁盘 Generation
  └── RetrievalPipeline：召回、融合和 Parent 上下文
```

### Repository 接口

- `save(snapshot, signature)`：保存新的独立目录，返回 `SavedGeneration(generation, signature)`；
  只有向量库和 SQLite 均写入成功才返回，不修改 current.json。
- `publish(saved)`：写入临时指针，再以文件 replace 更新 current.json。调用方须先准备好查询组件。
- `load_current(signature)`：签名匹配时加载；没有指针或签名不匹配返回 None，供 Facade 决定是否构建。
- `load_generation(generation)`：读取指定 Generation，不切换 current，也不加载 Embedding 模型。

Generation 文件仍为 faiss.index、chunks.jsonl、metadata.db；SQLite 表和指针 JSON 结构、
INDEX_VERSION=5 均不变。旧索引可直接加载，不需要迁移或重建。
签名继续由 Facade 使用原有效模型、切分参数和文档指纹生成，Repository 不猜测或改写签名。

### 新版本发布顺序

```text
处理文档并构建内存索引
  → 保存独立的新 Generation
  → 准备 Parent 映射与完整 RetrievalPipeline（含 BM25）
  → 原子发布 current.json
  → 安装已经准备好的内存引用
```

Facade 全程沿用现有 RLock。发布后只有引用赋值，不再执行模型/组件构造、解析或磁盘 I/O。
向量保存、元数据写入、查询组件构造失败时，旧指针与旧内存对象保持不变；
临时指针写入/替换失败时同样不切换内存。错误明确向调用方传播，不伪装成功。

旧 Generation 始终保留。失败可能留下未发布的构建目录或临时指针文件，本轮不自动清理，
它们不会被 load_current 当作当前版本。未增加自动恢复、回滚命令、多进程锁或后台切换。
这里保证正常进程内的发布顺序，不声称磁盘与内存组成跨进程/断电事务；其他运行中的进程
仍需显式重建或重启才能切换其内存索引。

### 独立复用

可以使用已有 IndexSnapshot，而不重新处理文档：

```python
from app.rag.indexing.snapshot_repository import SnapshotRepository
from app.rag.retrieval.pipeline import RetrievalPipeline

# 使用隔离目录演示，避免覆盖生产指针。
repository = SnapshotRepository("app/storage/repository-example")
# signature 应来自与 snapshot 一致的有效配置和源文件指纹，不用于猜测模型。
saved = repository.save(snapshot, signature)
prepared = RetrievalPipeline.from_index(
    snapshot.store,
    {parent.parent_id: parent for parent in snapshot.parents},
    embed=indexing.embed,  # 必须与该向量库使用同一编码模型
)
repository.publish(saved)
active_pipeline = prepared
restored = repository.load_current(signature)
```

KnowledgeRetriever 的旧构造参数、search、search_rankings、build_index 和 attach_index
保持不变；attach_index 仍只准备并绑定内存，不发布磁盘版本。没有改变解析/切分、Chunk ID、
默认 BGE-M3、向量库、Dense/BM25/RRF 算法、Top-K 或 API 响应格式。
前述第一、二步中的 _save/_load 描述为当时状态；本步已将它们移到 Repository，
并完成 Facade 整理，不是重建 RAG 框架。

本步验证：完整回归 139 passed、10 skipped（需显式启用的 PDF/OCR 模型测试默认跳过）。
直接加载历史 MiniLM 冻结 Generation，验证现有文件格式可读、另存后可发布且旧版本保留；
注入向量保存、SQLite 写入、查询组件准备和指针替换故障，旧指针和旧内存对象均保持可用。
成功路径测试明确核对 save → prepare → publish → activate 顺序。
另对 18 组真实 BGE-M3 查询和 FastAPI 路由做重构前后对照，排名、分数、上下文完全一致，
原生产 Generation 直接复用，没有重新解析或发布新生产版本。

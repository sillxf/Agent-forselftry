# Security RAG Benchmark 扩展与复现指南

## 1. 交付范围

- 旧 30 题仍在 `tests/rag_benchmark/dataset/`，核心问答、证据、状态不变；旧结果未覆盖。
- 扩展版在 `tests/rag_benchmark/v1/dataset/questions.jsonl`：100 题，90 道可答、10 道不可答。
- 主分类分布为英文 15、中文到英文 25、混合术语 15、同义/间接 15、技术干扰 15、不可答 10、多文档 5。
- 语言分布为英文 40、中文 45、混合术语 15；同义/干扰/多文档类别内同时有中英文题，避免题型完全绑定语言。
- 21 份冻结文档：原 9 份 + 12 份固定版本 ATT&CK 官方节选；未虚构正确知识，也未改变生产知识库。
- 所有 100 题及 100 条英文实验翻译均为 pending，审核人为空；AI 来源检查不是人工批准。

## 2. 数据结构与来源

兼容已有 Schema 2：`id` 就是 question_id；嵌套 `relevant_evidence[].evidence_id` 是唯一 Evidence ID 真值；
`Question.question_id`、`Question.evidence_ids` 提供只读访问，不另存一套可能不一致的标签。
新增 language、document_language、topic、question_type、design_note、query_family、hard_negative_sources。
不可答题保留空 relevant_evidence，不能把相似文档、RRF 分数或模型猜测当成证据。
完整来源、固定提交、SHA-256、许可证与节选范围见 `v1/manifest.json`、`v1/SOURCES.md`。
70 个新增设计与来源短引文分别在 question_designs.json 和 evidence_designs.json；evidence_catalog.json 为真实解析位置。

## 3. 审核入口

- [原集审查及覆盖报告](../tests/rag_benchmark/dataset/benchmark_expansion_report.md)
- [逐题 Ground Truth 清单](../tests/rag_benchmark/v1/dataset/review.md)
- [审核使用说明](../tests/rag_benchmark/dataset/benchmark_review_checklist.md)
- [机器可读覆盖统计](../tests/rag_benchmark/v1/dataset/coverage.json)

每题都列出问题、参考答案、原文、等价替代证据、Block ID、章节/页码、设计说明、干扰来源及对照实验英文 Query；翻译审核状态单独列出。审核复核答案完整性、等价证据、翻译忠实度及未知题缺口。
原 010/015/024/025 的参考表达问题仍如实保留为待审事项，没有为了提高分数私改旧题。
本集只有 63 个按文档+引文去重的事实，不应把 100 个语言变体视为 100 个独立事实；后续留出集应按共享事实聚类隔离。

## 4. 实际运行命令

```powershell
.\.venv\Scripts\python.exe scripts/run_rag_benchmark.py `
  --dataset tests/rag_benchmark/v1/dataset/questions.jsonl `
  --retriever all --top-k 5 --ks 1,3,5,10 --offline `
  --storage-dir app/storage/security-v1-minilm `
  --output-dir evaluation_results/new-security-v1-a
```

`--ks` 只取同一次最大深度（10）的排名前缀；候选上限使用 max(配置候选数, 10×4)，不是分别换候选池跑四次。
原命令不传 --ks 时维持原单 K 行为。Child 与 unique-Parent 分开计分；普通 Recall/MRR 排除不可答题。
输出原指标外，另有 multik_metrics.json、multik_report.md、failure_cases.json、failure_report.md；
每题原始 JSON 保存查询、策略、源 Block ID、检索单元 ID、排名、分数、命中 Gold Evidence ID 和未命中事实。
没有 Gold 匹配的片段仍保留真实 Chunk/Parent/Block ID，不凭空给它分配正向 Evidence ID。

## 5. 本次真实结果（r2 平衡语言候选版）

下表是 unique-Parent 宏平均，分母 90 道可答题，不是最终答案正确率。

| Strategy | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| dense | 0.4352 | 0.5250 | 0.5583 | 0.6028 | 0.1200 | 0.4954 | 0.5114 |
| bm25 | 0.3648 | 0.5267 | 0.5333 | 0.5444 | 0.1133 | 0.4519 | 0.4738 |
| hybrid | 0.4619 | 0.5472 | 0.5694 | 0.6028 | 0.1222 | 0.5204 | 0.5323 |

### Hybrid 分组 Parent Recall@5

| Group | Questions | Recall@5 |
| --- | --- | --- |
| question_type: english | 15 | 0.9333 |
| question_type: mixed_terms | 15 | 0.9333 |
| question_type: multi_document | 5 | 0.4500 |
| question_type: paraphrase | 15 | 0.7333 |
| question_type: technique_confusion | 15 | 0.6000 |
| question_type: unanswerable | 10 | N/A |
| question_type: zh_to_en | 25 | 0.0400 |
| language_pair: en->en | 35 | 0.9714 |
| language_pair: en->mixed | 1 | 1.0000 |
| language_pair: en->none | 4 | N/A |
| language_pair: mixed->en | 15 | 0.9333 |
| language_pair: zh->en | 39 | 0.0577 |
| language_pair: zh->none | 6 | N/A |

- Hybrid 的 10 道不可答题都返回了邻近上下文（返回率 100%）；BM25 为 60%。这说明检索不会自动识别知识缺口，不等于生成了错误答案。
- 没有生成器、相关性阈值分类器或 Agent Judge；“高相关性错误判断”和“正确拒答率”均留为 null。
- 同义组和术语组仍有容易题；这是暴露跨语言与技术邻近噪声的候选开发集，不是已完成难度校准的独立测试集。
- 旧的 92% 属于不同题数、语料与 K 设置；不能把本次较低分数当作生产代码退步。

## 6. 失败分析

[全部逐题失败/噪声报告](../evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm/hybrid/failure_report.md)。
语言相关原因只标为待验证假设，不能仅凭中文题失败就宣称已确定 Embedding 根因。
“前 10 没有正向证据”也不等于完整候选池或整个语料没有该证据。

### Top-10 内完全未命中：35 题（维度可重叠）

- rag_011：暴力破解告警的本地响应清单建议采取哪些措施？；首个正向 Parent 排名 None；原因 required_evidence_absent_from_saved_top_10, cross_language_mismatch_hypothesis_not_proven
- rag_014：本地 SQL 注入知识库列出了哪些预防措施？；首个正向 Parent 排名 None；原因 required_evidence_absent_from_saved_top_10, cross_language_mismatch_hypothesis_not_proven
### 正确证据排名靠后：3 题（维度可重叠）

- rag_004：Which OWASP WSTG test identifier covers SQL injection?；首个正向 Parent 排名 6；原因 relevant_evidence_ranked_below_cutoff
- rag_049：数据库结果不直接出现在页面中时，测试者可以通过什么观察方式重建信息？；首个正向 Parent 排名 6；原因 relevant_evidence_ranked_below_cutoff, cross_language_mismatch_hypothesis_not_proven
### 存在已声明相似干扰来源：7 题（维度可重叠）

- rag_076：What account attack tries the same few common passwords across identities to avoid per-account lockout?；首个正向 Parent 排名 1；原因 known_similar_but_wrong_source_returned
- rag_078：Which technique uses a stolen hash to authenticate directly rather than cracking it back into a password?；首个正向 Parent 排名 1；原因 known_similar_but_wrong_source_returned

干扰来源即使与正确来源同时返回，也只是上下文噪声信号，不自动算作题目回答错误。

## 7. A / B / C 实验

- **A 已完成**：现有 MiniLM + Hybrid；另跑 Dense/BM25 作诊断，不改生产默认。
- **B 已具备执行代码，尚未运行**：BGE-M3 + 原 Hybrid。
- **C 已具备执行代码，尚未运行**：BGE-M3 原问 Dense + 英文翻译 Dense + 英文 BM25 + RRF60。
- B/C 复用 A 的冻结 Chunk 文本、ID、Parent 和同一 Ground Truth，只重建 BGE 向量；B/C 查询和索引都用 BGE，不与 MiniLM 向量混用。
- 当前本地没有 BGE-M3 缓存；本次选择离线运行，没有自动下载、更换生产模型，也没有填入 B/C 分数。
- 英文原问与英文翻译相同时去重 Dense 路由；C 的非英文题最多三路，额外计算成本与路由候选逐题记录。
- BGE 原生上下文能力未在此利用：为控制变量，使用 MiniLM 冻结的短 Chunk；不能据此代表所有 BGE 配置。

```powershell
.\.venv\Scripts\python.exe scripts/run_security_rag_comparison.py `
  --baseline evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm `
  --output-dir evaluation_results/new-security-v1-bc --offline
```

需要实际运行 B/C 时，先明确决定下载评测权重，可执行：

```powershell
# 在未设置 HF_HUB_OFFLINE / TRANSFORMERS_OFFLINE 的终端中下载一次；不修改应用配置
.\.venv\Scripts\python.exe -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('BAAI/bge-m3')"
```

缓存完整后再执行同一离线命令。实际模型 revision、权重/Tokenizer SHA、索引哈希、Chunk 参数、排名深度、RRF 参数和源码快照会写入配置。
状态记录：[当前 B/C 未运行原因](../evaluation_results/baselines/2026-11-01_security_v1_balanced_model_comparison/status.json)。
配置清单：`tests/rag_benchmark/v1/experiments.json`。Cross-Encoder 不在实验中。

## 8. 来源重建与审查复跑

正常评测不需要重新生成题目；冻结输入已经提供。仅需检查时：

```powershell
.\.venv\Scripts\python.exe -m evaluation.rag.coverage_audit
```

如需在另一份工作副本中从来源重建：

```powershell
# 仅当固定 STIX 源不在缓存时，显式下载固定提交并验证 SHA
.\.venv\Scripts\python.exe -m evaluation.rag.expansion --download-source --prepare-corpus
# 仅用于尚无 questions.jsonl 的新生成目录，拒绝覆盖已存在的标签
.\.venv\Scripts\python.exe -m evaluation.rag.expansion --materialize
```

question_designs.json 是人工可读的 AI 设计输入；compose_questions 的结果与实际 JSONL 有一致性测试。任何人工修订应另记新版本，不能用生成器覆盖。
当前 v1 目录名称不随修订变化，但 metadata version=r2、SHA 和 design_revisions.json 明确记录 14 道新增题的语言平衡修订。首轮运行保留用于审计，不可与 r2 当作同数据模型对照。

## 9. 范围与后续

所有新增能力只在 evaluation/ 与评测入口，app/ 和生产 Embedding、检索算法没有修改。
接下来应审核候选题/英文翻译，补齐 BGE 缓存后完成同数据 B/C 对比，并另建按事实族隔离的留出集；不要先引入 Cross-Encoder 或直接替换生产模型。

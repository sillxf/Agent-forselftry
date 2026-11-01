# RAG Benchmark 第二阶段报告（2026-11-01）

**结论：标注修正、评测工具、对照实验、PDF 回归和 Agent 设计已交付；本阶段尚不能宣布全部验收完成。**
30 题仍待真实人工审核，正式 `--require-reviewed` 基线尚未生成。全模型测试虽然 91 项断言通过、退出码为 0，但日志出现 Windows 原生访问违规诊断，根因未定，不能宣称原生链路完全稳定。

## 1. 完成范围

| 项目 | 实际状态 |
| --- | --- |
| 表格规则事实 ID、事实粒度与中英等价位置检查 | 已做 AI 来源核查；3 个错误 ID 修正；有争议处保留人工决定 |
| 人工相关性审核 | **0/30 批准**，reviewer 全为空；未自动代签 |
| 指标与单元测试 | 保持 result-qrels-v2；补齐多 alternatives、Parent 多事实、重复事实、空结果、不可答、不同 K 和单位测试 |
| Dense / BM25 / Hybrid 对照 | 同数据、语料、Chunk、Embedding、K=5 完成；**候选结果，非正式验收** |
| A/B/C/D 中文实验 | 2 题 × 4 组 × 3 策略，共 24 条独立结果；原始问题未变 |
| PDF 结构修复 | 字体保留、图表容器、编号层级、定义正文、受限双栏顺序修复；离线与原 PDF 回归均覆盖 |
| 常规 CI | 已验证工程提交成功；PDF/OCR 模型步骤被跳过，不能冒充远程全量模型测试通过 |
| Agent Evaluation | 仅设计与 8 个候选案例；**没有执行结果、拒答率或幻觉率** |

## 2. Dataset Audit Report 与变更记录

当前版本：`rag-benchmark-v0.3.1-structure-corrected-candidate`；Schema 2 不变。9 份语料、30 个原问题、参考答案和评分口径均不变。
v0.2 Dataset SHA-256：`070cda0b190aa3b41f2ad058ecf9a28f1190e6d11c693fcb5f776646cbb38cbf`。
只修 ID 后 SHA-256：`348ab0951186a1c873a7209cf3c378e13af215d74f31d8f6df141e7b4d1adbfc`。
修正结构定位后的最终 SHA-256：`04cadb9bab07b00e64a2e2011274493497dc9e64d4e63ef945a5e60128dee3b7`。

| 题目 | 原事实 ID | 修正后 | 理由 |
| --- | --- | --- | --- |
| rag_005 | `continued_rules-b1-1` | `continued_rules-r002` | R002/R003/R004 是不同规则，不是同表同一事实 |
| rag_016 | `continued_rules-b1-1` | `continued_rules-r004` | R002/R003/R004 是不同规则，不是同表同一事实 |
| rag_017 | `continued_rules-b1-1` | `continued_rules-r003` | R002/R003/R004 是不同规则，不是同表同一事实 |

- 三道规则题的原问答、行引用及 grade 完全保留，不能将不同表格行放进 alternatives。
- rag_011/014：保留三项完整清单，冻结英文指南里没有中文重复位置，不凭翻译虚构 alternatives。
- rag_012：凭据与干净备份是两个必要动作，不加未问及的其他动作。
- rag_015：保留及时分享建议、现代事件复杂/耗时、持续改进必要性三项；why 问题的分母边界仍须人工确认，没有为提高 Recall 删除事实。
- rag_018：三项动作的中英版本是各自同一事实的 OR 位置，不是六项要求。rag_021：两个英文 out-of-band 定义属于同一事实的等价位置，并非中英重复。
- rag_024/025：保留跨账户信号与处置清单、访问控制绕过与权限跨账户风险；它们是参考知识，不能变成当前事件事实。
- rag_026–030：逐份检查冻结资料的范围并查询指定实体/日期；没有私有 API key、指定虚构漏洞 IOC、指定日期登录账户、私有固件命令或 ACME 损失数据。相似 IOC、示例密码与一般指导不能填补这些空白。自动检查仍不是人工语义批准。
- rag_010/015/022 共 6 个 NIST 证据位置只更新 section_path；引用、Block ID、页范围、grade 和事实语义不变。
- 新校验拒绝同一个 evidence_id 指向不同事实；旧实验结果和旧数据快照没有重写。历史 flawed 数据须搭配它自己的冻结实现重放。

详细记录见 `tests/rag_benchmark/dataset/phase2_audit.md`、`phase2_annotation_changes.json`、`phase2_structure_location_changes.json`、`phase2_review_notes_changes.json`。
实验目录 `evidence_mapping.json` 保存 30 题、43 个题内必要事实、47 个主/替代来源位置到实际 Child/Parent ID 的映射。**43 是各题要求的累计数，不是整个语料去重后的事实数。**
`annotation_snapshot/` 是运行时原件，保持不动；之后将审核文字里的历史 PDF 缺陷与当前状态明确区分，最新单据单独放在 `review_packet/`，附前后哈希。问答、标签、批准状态和指标没有改变。

## 3. 评分边界

- Recall@K：唯一必要事实覆盖率，OR 位置不增加分母；同一事实重复命中不多算 Recall。
- Precision@K：相关结果位 / 固定 K，不用“新事实数”替代结果数。
- MRR@K：第一个相关结果的真实排名倒数，空位和不相关位不删除。
- NDCG@K：每个结果取命中事实的最高 grade，gain=2^grade−1；DCG 与 IDCG 使用同一种 Child 或 Parent 单位，IDCG 从该类型的完整索引 qrels 得到。
- Parent 一次包含多项事实不按事实数量重复惩罚。qrels 是源引用/原始 Block 派生的，不冒充人工逐 Chunk 相关性标签。
- 本轮没有修改 `retrieval_metrics.py` 或 result-qrels-v2 定义。只命中章节元数据、没有正文引用，不计正文证据。
- 5 道不可答题不进入普通 Recall/MRR/NDCG 的 25 道可答题宏平均。返回邻居不代表回答，更不代表拒答正确。

## 4. 三策略实际结果（K=5，候选）

### Child Retrieval Metrics

| Strategy | Recall@5 | Precision@5 | MRR@5 | NDCG@5 |
| --- | ---: | ---: | ---: | ---: |
| dense | 0.8400 | 0.2160 | 0.6733 | 0.7166 |
| bm25 | 0.8800 | 0.2080 | 0.6913 | 0.7142 |
| hybrid | 0.8800 | 0.2240 | 0.8133 | 0.8305 |

### Parent Retrieval Metrics

| Strategy | Recall@5 | Precision@5 | MRR@5 | NDCG@5 |
| --- | ---: | ---: | ---: | ---: |
| dense | 0.9200 | 0.1920 | 0.7733 | 0.8127 |
| bm25 | 0.8800 | 0.1840 | 0.6980 | 0.7466 |
| hybrid | 0.9200 | 0.1920 | 0.8600 | 0.8757 |

本小样本中 Hybrid 的 MRR/NDCG 较高，但 Child Recall 与 BM25 相同；不能预设混合一定更好，更不能把两张表合成一个分数。

## 5. Child / Parent 与失败诊断

| Strategy | Child 命中但 Parent 漏掉（题数） | Parent 命中 Child 未命中（题数） |
| --- | ---: | ---: |
| dense | 0 | 2 |
| bm25 | 0 | 0 |
| hybrid | 0 | 1 |

- Dense 的 rag_004/020、Hybrid 的 rag_004 出现 Parent 找回额外事实；这证明更大上下文有时能补回内容，不证明其余文本没有噪声。上下文噪声对生成的影响本轮未评估。
- rag_004：正确 OWASP 标识表格 Child 在 Hybrid 候选第 26，Dense 第 13，均不在 Top 5；证据并没有丢失。BM25 全索引诊断中正确行排第 229，虽与原 Query 有 SQL/injection 词重叠，仍未进原 20 项稀疏候选。
- 自动归因最初把 rag_004/BM25 的候选缺失标成 Lexical Mismatch **假设**；后续全稀疏排序证据表明应归为候选排序/截断问题。原自动报告不覆盖，修正见 `sparse_candidate_addendum.json` 与 `failure_classification_addendum.json`。扩池只用于诊断，没有进入任何主指标。
- rag_002/003：Hybrid 正文证据分别排第 2/3；通用标题或仅含答案名字的 metadata 不能替代正文支持。
- rag_016：正确 R004 行为 Hybrid 第 2；同表另一行即使共用来源 Block，也不算支持 High/Block，完整行引用仍须匹配。
- rag_011/014：原中文 Query 在三种策略中均漏掉正确证据。下面四组实验区分语言匹配与融合排序问题，不直接替换原问题。
- 共 28 条失败题×策略记录。经上述具体诊断修正后，22 条涉及排序，6 条原中文检索失败；这是当前证据支持的分类，并不是其他缺陷在全系统被证明不存在。词法/语义原因属于假设时都明确注明。
- JSON 逐题保留原 Query、策略、正确引用、实际 Child/Parent Top K、来源和 Chunk ID、候选排名、原因与建议；完整类别包括 Lexical/Semantic/Cross-lingual、Chunk Boundary、Parent Recovery、Metadata/Structure、Ranking、Evidence Annotation。
- 不可答题单列 15 条题×策略邻近结果及误用风险，不能从一般指导推断当前事件。是否识别知识缺口、是否编造/拒答，均明确 `not_evaluated`，留给 Agent Evaluation。

## 6. 中文跨语言实验

A=中文+当前模型；B=固定英文翻译+当前模型；C=中文+多语言模型；D=中文/英文双路、当前模型、查询级等权 RRF。原问题均未改，翻译文本另存；未把实验组混入主 Benchmark。
当前模型：`all-MiniLM-L6-v2`，revision `1110a243fdf4706b3f48f1d95db1a4f5529b4d41`。
多语言模型：`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`，revision `e8f8c211226b894fcb81acc59f3b34ba3efd5f42`。

以下均为 rag_011/014 的两题宏平均；BM25 的完整控制组另见实验子报告。

### Child 跨语言独立结果

| Strategy | Group | Recall@5 | MRR@5 | NDCG@5 | Mean latency ms |
| --- | --- | ---: | ---: | ---: | ---: |
| dense | A | 0.0000 | 0.0000 | 0.0000 | 8.7012 |
| dense | B | 1.0000 | 1.0000 | 1.0000 | 8.5171 |
| dense | C | 1.0000 | 0.2667 | 0.4434 | 15.2484 |
| dense | D | 1.0000 | 0.7500 | 0.8155 | 17.6749 |
| hybrid | A | 0.0000 | 0.0000 | 0.0000 | 11.9704 |
| hybrid | B | 1.0000 | 1.0000 | 1.0000 | 10.1011 |
| hybrid | C | 0.0000 | 0.0000 | 0.0000 | 18.2196 |
| hybrid | D | 1.0000 | 0.2917 | 0.4653 | 22.7348 |

### Parent 跨语言独立结果

| Strategy | Group | Recall@5 | MRR@5 | NDCG@5 | Mean latency ms |
| --- | --- | ---: | ---: | ---: | ---: |
| dense | A | 0.0000 | 0.0000 | 0.0000 | 8.7012 |
| dense | B | 1.0000 | 1.0000 | 1.0000 | 8.5171 |
| dense | C | 1.0000 | 0.2667 | 0.4434 | 15.2484 |
| dense | D | 1.0000 | 0.7500 | 0.8155 | 17.6749 |
| hybrid | A | 0.0000 | 0.0000 | 0.0000 | 11.9704 |
| hybrid | B | 1.0000 | 1.0000 | 1.0000 | 10.1011 |
| hybrid | C | 0.0000 | 0.0000 | 0.0000 | 18.2196 |
| hybrid | D | 1.0000 | 0.2917 | 0.4653 | 22.7348 |

两题的 Child/Parent 恰好得到相同数值，但评分分别执行，不能推广成两种单位等价。
- B：三种策略均 Recall/MRR/NDCG=1，是值得扩样验证的方向；翻译仅改变语言表达，没有添加 IP/MFA/预编译语句等答案词。翻译的语义检查由 AI 完成，人工确认仍未完成。
- C：Dense 找回两题，正确结果分别第 5/3；接入现有 Hybrid 后两题正确结果均到第 6、掉出 Top 5。**不能把多语言向量命中直接等同于混合检索改善。**
- D：能找回事实，但本轮 Hybrid 的 MRR/NDCG 不如英文单路，且有两路候选与额外耗时，不能声称性价比更高。
- 索引成本：主索引设置/构建 47.071s；C 模型加载 3.234s，固定 Chunk 的新向量/FAISS 建立 4.647s，CPU 35.562s，索引 731978 bytes。
- 全部组复用相同 272 条 Chunk 内容/ID；不按多语言 tokenizer 重切。C 的 max_sequence_length=128，有 40 条长输入会截断，已记录，不能将结果泛化为该模型在所有切分设置上的表现。
- 延迟为加载/建库之后每组 5 次热运行，轮换顺序，记录原始 samples/first-run/P50/P95；不是严格隔离硬件的统计显著性实验。预先固定翻译不包含在线翻译服务的耗时/费用。D 使用双倍路由，不是等算力比较。

**配置决定：** 先扩样验证 B 的忠实翻译；C 暂不替换默认模型；D 暂不默认启用；目前没有证据支持再引入 Query Expansion 或 Reranker。只有 2 道开发题，不能据此改生产默认值。下一轮可单独研究多语言 Dense 与稀疏融合的排序，不混改多个变量。

## 7. PDF 结构修复与回归

1. 查看了原 NIST 三页、Docling 原始结构以及实际字体/cell。原 PDF 和原始 Docling 快照没有改写。
2. 打开 generate_parsed_pages，让当前本来为空的 page.cells 在生成 Block 前仍可读取字体信号，避免丢掉真正标题的粗体特征。
3. 保存 picture/table 容器及原标签，图中文字和 caption 不参加章节推断；“Containment”保留为图中文字，不再污染后续 section_path。
4. 将定义引导句而非标题保留为正文；按编号/粗体/后续正文恢复 1. Introduction、1.1 Purpose and Scope，并恢复 2 / 2.1 的层级。原始与推断标题仍分别记录。
5. 新增真实双栏 PDF：Docling 原始顺序把两列标题提前、导致左列正文落入右列章节。只在两标题对齐、两边都有正文且存在不相交栏间距时恢复按栏顺序；跨栏正文、图表和复杂版式仍保留上游顺序，不宣称全面解决多栏问题。
6. 离线回放真实 Docling 文档/cells 进入生产 Parser/Merger/StructureRecovery；额外用模型直接解析原 PDF。覆盖正常标题、图内标题文字、正文编号、表格 caption、双栏、跨页续接及层级恢复。原有 15 份混合格式语料仍参与完整回归。
7. 索引版本提升到 5，避免旧缓存掩盖修复；未改 Retriever 排序、生产 Embedding、默认 K 或向量库。没有文档名称特判，也没有逐段让 LLM 编标题。

## 8. 可复现性与记录

工程 Git SHA：`7dbd41eec127f13fa442181e9a5f18eb419b4503`；pipeline version 5；source SHA-256 `07e73e2260450350d0ea5e1089177016d313f53e86fb10e4632c187ac7b3cb14`。
Corpus manifest SHA-256：`e5ed786f01adaf8544c70402773741991b4a31d71e5edabadd9c1d2ceab5e375`。
主对照共享同一个索引、模型权重/Tokenizer 指纹、Chunk 参数、RRF=60、Dense/BM25 候选=20、Top K=5、评分口径。配置与原始结果全部保存。
独立重放从封存 documents/ 而非原目录重新解析、切分、建向量索引并跑 90 次检索；三策略所有排名、分数、事实命中、qrels、指标、诊断、可移植 Chunk 指纹和 FAISS 向量字节相同。只排除延迟与本地图片存储路径比较，不声称跨机器位级相等。
`index_snapshot/` 保存主索引，`crosslingual/multilingual_index/` 保存 C 索引；数据/语料/Manifest、原始排名、失效来源映射、源码 ZIP、模型 revision/权重/Tokenizer 指纹、配置、日志及重建配置均留存。只看模型名不足以重放，应冻结配置中的 revision/权重。
运行时 dirty=true 是如实记录（本地交接文件/实验输出等未提交）；source_snapshot.zip 归档的是当时准确的 app/scripts/requirements 字节，已核对与工程代码一致。交接文档、模型权重和本地缓存不在提交中。

```powershell
python scripts/run_rag_benchmark.py --retriever all --top-k 5 --offline `
  --storage-dir app/storage/benchmark-phase2 --output-dir evaluation_results/new-candidate
python scripts/analyze_rag_benchmark.py --baseline evaluation_results/new-candidate `
  --storage-dir app/storage/benchmark-phase2
python scripts/run_crosslingual_experiment.py --baseline evaluation_results/new-candidate `
  --storage-dir app/storage/benchmark-phase2 --output-dir evaluation_results/new-crosslingual --offline
# 人工批准、更新数据版本后才可正式运行：
python scripts/run_rag_benchmark.py --retriever all --offline --require-reviewed
```

## 9. 测试与 GitHub Actions

| 验证 | 实际结果 | 不能过度声称的地方 |
| --- | --- | --- |
| 常规本地完整收集 | **81 passed，10 skipped**，退出 0 | 10 个 PDF/OCR 模型用例未在普通命令运行 |
| --rag-models 完整运行 | **91 passed，0 skipped**，退出 0 | **出现 access violation 诊断，不能叫完全干净通过** |
| PDF 回归单独复查 | **9 passed**，退出 0，无访问违规日志 | 单独复查干净不证明全量间歇问题已修复 |
| pip check / compileall / diff check | 通过 | 不等于模型原生库稳定性保证 |
| --require-reviewed 门禁 | 正确拒绝 30 pending；未创建模型索引或输出目录 | 没有绕过人工门禁生成正式基线 |
| GitHub Actions | run **41286832600**，commit **7dbd41e**，**success** | 仅常规 pytest，Full corpus including PDF and OCR 步骤 **skipped** |

访问违规出现在完整日志开头，栈仅到 Pydantic 构造且不完整，无法据此断定具体原生组件。旧版本已记录过间歇风险，本轮未证明根因、也未用跳过/屏蔽日志或大规模换依赖来伪装解决。完整失败诊断、XML 与独立复查原样保存。
上述 CI 是本次实验使用的工程提交；最终报告/制品提交会再触发自己的常规 CI，最新提交号与在线结果在交付回复中核对。

## 10. Agent Evaluation 设计（未实现）

设计见 `docs/agent_evaluation_design.md`，8 个初始候选案例见 `tests/agent_evaluation/cases.jsonl`。仅设计输入、允许/禁止事实、证据类别和人工评价维度，未运行 Agent、未改生产协议。
维度分别为 Alert Understanding、Evidence Grounding、Hallucination、Risk Assessment、Response Quality、Abstention。将 observed_event、reference_knowledge、supported_inference、unverified_hypothesis 区分；MITRE/NIST 不能当作当前告警的已观察事实。建议分别做固定证据生成测试、端到端测试、知识缺口/相似 IOC/空工具结果测试。

## 11. 未完成事项与下一步

1. **真实人工审核 30 题与 2 条翻译**，重点确认 rag_015 必要事实边界、其他等价来源、grade、正文/metadata 口径及不可答依据。未完成之前不批准正式基线。
2. 定位 Windows 原生访问违规：保留完整日志和环境，分离完整模型组/单模型组/进程生命周期调查；不要把“断言都过了”或某次重跑干净当作问题已修复。
3. 人工确认后更新 Dataset 版本，用 --require-reviewed 跑正式基线，另建未调过参的多样留出集。
4. 扩充忠实翻译/多语言/多路实验问题，再单变量检查稀疏候选截断与融合排序；不据两题直接换生产配置。
5. 表格逐行页码、复杂跨栏/图表布局、上下文对最终答案的噪声影响尚未解决；当前只保留可靠页范围。
6. Agent Runner、逐 claim 归因、风险/建议/拒答实际评测尚未实现。本轮设计不是这些能力已完成的证据。
7. 本轮没有加入 Reranker、VLM、知识图谱、Qdrant、多 Agent 或大规模 Embedding 微调。

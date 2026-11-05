# 可选离线评测

评测不参与服务启动，不调用付费模型。运行结果写入 `evaluation/results/`（Git 忽略）。

## 冻结基准：benchmark/security-v1

从 Git 历史恢复的 Security RAG Benchmark V1：100 题、21 份文档（MITRE ATT&CK、OWASP WSTG、NIST 节选及结构测试样例），版本 `security-rag-benchmark-v1-100-candidate-r2`。题目和证据由 AI 编写，**尚无人工审核**，结论只能作为候选参考。来源与许可见 `SOURCES.md`、`SOURCES_original9.md`、`licenses/`。文件按字节冻结（`.gitattributes` 禁止换行转换），实验开始时逐个校验 `manifest.json` 中的 SHA-256。

留出集：按 `query_family` 的稳定哈希划出约 20% 的题族（16 道可回答题），同一问题的不同语言变体始终在同一侧。留出集只用于确认，不用于选择参数。

## 分块参数实验：chunking_experiment.py

问题：产品默认 child 400 / parent 1600 / overlap 60 是否合适。使用当前产品的解析、分块、BGE-M3 Dense、BM25 和 RRF 代码，不用重排，不用 LLM。每组同时测两种查询方式：只用原问题，以及原问题加 `english_queries.json` 中的英文翻译（等同于调用方使用 `queries` 字段）。

~~~powershell
.\.venv\Scripts\python.exe -m evaluation.chunking_experiment --output evaluation/results/chunking-<日期> --offline
~~~

中断后用同一个输出目录重跑会复用已解析文档和已编码向量。

### 2026-11-06 结果

环境：Linux 2 核 CPU，docling 2.145.0、transformers 5.19.0、sentence-transformers 6.1.0、torch 2.14.1，与本机 Windows 依赖版本一致；BGE-M3 revision `5617a9f6`，权重 SHA-256 与历史报告一致。71 个 Parent。开发集 74 道、留出集 16 道可回答题全部计分。单位为百分比，Parent 粒度。

| 配置 | 开发集 R@5 | 开发集 MRR@5 | 留出集 R@5 | 留出集 MRR@5 |
| --- | ---: | ---: | ---: | ---: |
| child200，仅原问题 | 94.26 | 76.46 | 93.75 | 70.00 |
| child400（默认），仅原问题 | 91.89 | 73.76 | 93.75 | 69.48 |
| child800，仅原问题 | 91.89 | 72.91 | 87.50 | 68.23 |
| child200，加英文查询 | 97.30 | 91.49 | 100.00 | 88.75 |
| child400（默认），加英文查询 | 100.00 | 89.23 | 100.00 | 85.62 |
| child800，加英文查询 | 97.30 | 87.66 | 93.75 | 84.38 |

首轮运行发现 rag_019 的证据无法定位：Docling 把跨页句子的前半句“The authentication rule checks events,”识别成了章节标题，句子被拆到两个章节。已修复（以逗号、分号结尾的长句不当作标题，见 tests/test_structure_recovery.py），其余 20 份文档的解析结果逐块对比不变。上表是修复后的结果。

结论：

1. 调用方补充一条英文查询的收益最大：默认分块下开发集 MRR@5 从 73.76 升到 89.23。这证实了 `queries` 字段的价值，调用方 LLM 应该为中文问题补一条文档语言的查询。
2. 分块长度的影响在 2 到 3 道题之内，而且方向不稳定。只用原问题时 child200 略好（按预设停止规则判为“可切换”）；加英文查询后 child200 的开发集 R@5 反而低 2.7 个百分点（rag_009、rag_074 掉出前 5）。预设规则只看了原问题路径，没有覆盖推荐用法。
3. 因此**保持默认 400 不变**。child800 在留出集上 R@5 下降，不建议调大。
4. 局限：语料只有 21 份、多为短文档，基准未经人工审核，接近饱和。分块问题的最终判断需要更长、更真实的文档和人工审核过的题目。

## 压测：scripts/load_test.py

见脚本说明。2026-11-06 在 2 核 CPU 上的实测（BGE-M3 本地向量，12 份短文档，不开重排）：单并发 p50 约 430 ms，约每秒 2.4 次；8 并发时修复前 80 个请求中 75 个立即返回 503，加入最多 10 秒的排队后 80 个全部成功，p50 约 3.3 秒，吞吐不变。吞吐上限来自串行的本地模型推理，提高吞吐需要把向量模型移到独立推理服务或 GPU。

## metrics.py

纯指标计算（result-qrels-v2）：Recall 按唯一必要事实计，Precision/MRR/NDCG 按结果位计。

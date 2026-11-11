# BGE-M3 跨语言检索实验：交付与复现

## 本次范围

仅执行 Security Benchmark V1 的 B/C 检索实验，与既有 A 基线比较。
不修改生产配置、Benchmark、Ground Truth、MiniLM 索引或历史结果；不开展人工审核、Cross-Encoder、答案生成、Agent 拒答或其他模型实验。

## 结果入口

- [A/B/C 同表报告](../evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/abc_report.md)
- [机器可读指标和耗时](../evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/abc_comparison.json)
- [C 的残留失败分析](../evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/C_failure_analysis.json)
- [B 的完整结果](../evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/B/retrieval_results.jsonl)
- [C 的完整结果](../evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/C/retrieval_results.jsonl)
- [本次英文 Query 快照](../evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/english_queries.json)
- [翻译副本变更记录](../evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/translation_changes.json)

## 模型与控制变量

- 实际模型：BAAI/bge-m3，revision `5617a9f61b028005a4858fdac845db406aefb181`，CPU / float32，1024 维归一化 Dense 向量。
- 直连 Hugging Face 超时，使用 hf-mirror.com 下载同一仓库的固定版本；2,271,145,830 字节权重文件 SHA-256 已对照官方文件页核实：`b5e0ce3470abf5ef3831aa1bd5553b486803e83251590ab7ff35a117cf6aad38`。
- 模型留在本机 Hugging Face 缓存，不放入 Git；下载来源、逐文件 SHA、耗时见 model_source.json 和 model_download.log。
- 复用 A 的 301 个 Child、70 个 Parent、21 份语料与 100 题。保持相同 Ground Truth、search_text、Chunk ID、BM25Plus、候选上限、Top-K 和 RRF60。
- A 原配置的 effective_child_max_tokens=254 表示冻结切分边界；BGE 不重切文档，模型本身 max_sequence_length=8192。两者配置分别记录，不将模型原生长度误报成切分参数。
- B、C 共享新建的 bge_index，不混入 MiniLM 向量。索引编码 batch=4 仅控制内存，不改变数据或排名参数。
- 中文、混合语言题按原问 Dense + 英文 Dense + 英文 BM25 融合。40 道英文原问与翻译一致，去重为两路；其余 60 道三路。

## 翻译处理

复用原有 100 条英文 Query，复制到本实验输出目录；原文件未改。
在副本中修正 rag_055/060/062/063 的安全记号或条件遗漏，分别保留 `.bat/.cmd`、Windows service/SCM、breach dump 认证失败条件及 `Pass-the-Hash` 拼写。
变更只依据原问题，不添加答案或证据；逐条前后文本、设计理由和仍为 pending 的状态保存在 translation_changes.json。
识别到的 CVE、ATT&CK ID、IP、Hash、规则 ID、命令/代码等字面保留检查见 translation_identifier_checks.json；测试集没有覆盖所有标识符样式，不据此宣称翻译器具备普适保真保证。

## 复跑（保留旧结果，写新目录）

本机权重已缓存。先确认缓存仍是本次固定版本：

```powershell
.\.venv\Scripts\python.exe -c "from pathlib import Path; from huggingface_hub import try_to_load_from_cache; p=try_to_load_from_cache('BAAI/bge-m3','config.json'); assert isinstance(p,str) and Path(p).parent.name=='5617a9f61b028005a4858fdac845db406aefb181', 'BGE cache revision changed or missing'"

.\.venv\Scripts\python.exe scripts/run_security_rag_comparison.py `
  --baseline evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm `
  --translations evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/english_queries.json `
  --output-dir evaluation_results/new-bge-m3-bc `
  --index-batch-size 4 --offline
```

脚本自动生成 B/C 原始排名、分组指标、失败报告及 A/B/C 表。
模型缓存缺失时先按 model_source.json 指定版本下载并校验，不要用其他模型或未经核对的新版本填补。
仅重新生成汇总报告、不重新检索：

```powershell
.\.venv\Scripts\python.exe -m evaluation.rag.comparison_report `
  --baseline evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm `
  --output-dir evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc
```

## 解释边界

主表是 unique-Parent 的必要事实覆盖指标，不是答案正确率。中文→英文分组有 39 道可回答题，跨越主分类；不是仅 question_type=zh_to_en 的 25 题。
C 全部可回答题 Recall@5=98.89%，中文→英文 Recall@5=100%；不能外推为生产满分。此公开开发集仍有共享事实/语言变体，标签仍是原候选状态。
C 唯一 Top5 缺失是 rag_009：标注正向 Child 在 Dense 第 16、BM25 第 2，RRF 后对应 Parent 第 6；前 5 均为同一 OWASP 文档的其他章节。Top10 已命中，没有擅自新增替代证据来抬高分数。
耗时不包含翻译生成：C 使用冻结翻译。A 是历史运行，B/C 为本次 CPU 运行，不能当成严格受控并发性能对照。

## 实际代码变更

1. `evaluation/rag/model_comparison.py`：内存友好的索引批次、实际时间/运行环境记录、沿用 A 参数，并自动汇总 A/B/C。
2. `evaluation/rag/comparison_report.py`：新增统一指标表、语言分组变化、耗时和 C 的真实残留失败分析。
3. `evaluation/rag/provenance.py`：用连续张量的零拷贝内存视图计算 SHA，避免为大模型权重指纹额外复制大块内存；哈希字节协议不变。

其余新增内容为本说明和独立实验产物，不是生产检索算法变更。

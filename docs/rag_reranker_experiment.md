# BGE Reranker 实验一

日期：2026-11-02  
状态：已完成，Multi-View 未参与。

## 实验设置

```text
BGE-M3 Dense + BM25Plus + RRF
        ↓
固定 Hybrid Top 20
        ↓
BAAI/bge-reranker-v2-m3
        ↓
最终 Top 5
```

A、B 使用同一份 Security RAG Benchmark V1、同一 Ground Truth、同一 BGE-M3 Child 索引、同一 Chunk 和 BM25/RRF 参数。显式 `candidate_k=20` 表示融合后的最终候选池为 20，不是 Dense 20 与 BM25 20 的并集。

复现命令：

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
.venv\Scripts\python.exe scripts\run_reranker_experiment.py `
  --offline `
  --output-dir evaluation_results/reranker_experiment_2026-11-02_v3
```

完整逐题结果、Reranker 分数和排名变化保存在本地输出目录：
`evaluation_results/reranker_experiment_2026-11-02_v3/`。

## 结果

90 道可回答题进入普通检索指标，10 道不可回答题不计入 Recall/MRR/NDCG 平均。两组均为 100 题、0 查询错误。

| 方案 | Parent Recall@5 | Parent Recall@10 | Parent MRR@5 | Parent NDCG@5 |
| --- | ---: | ---: | ---: | ---: |
| A：Hybrid Top 20 | 94.44% | 97.78% | 74.35% | 79.57% |
| B：Hybrid Top 20 + BGE Reranker | 96.94% | 98.89% | 92.26% | 93.33% |
| 变化 | +2.50 个百分点 | +1.11 个百分点 | +18.91 个百分点 | +13.76 个百分点 |

中文问题 → 英文文档分组：

| 方案 | Recall@5 | MRR@5 | NDCG@5 |
| --- | ---: | ---: | ---: |
| A | 92.31% | 53.85% | 63.89% |
| B | 92.95% | 83.42% | 85.94% |

英文问题 → 英文文档分组：

| 方案 | Recall@5 | MRR@5 | NDCG@5 |
| --- | ---: | ---: | ---: |
| A | 97.14% | 88.33% | 90.55% |
| B | 100.00% | 100.00% | 99.57% |

## 变化分析

在可回答题中，Reranker 新增召回了 `rag_009`、`rag_014`、`rag_031`、`rag_079`，但使 `rag_049`、`rag_100` 的必要证据覆盖下降。也就是说，收益主要是把已进入 Hybrid Top 20、但原始 RRF 排名靠后的正确 Child 提前；它没有解决候选池之外的召回问题，也不是无条件提升。

Reranker 在本机 CPU 上的 B 组平均查询耗时约 `9028 ms`，A 组约 `192 ms`。这只是当前 CPU、批处理和本地负载下的工程测量，不代表生产部署性能。该成本需要在决定是否开放给 Tool 调用前单独评估。

本实验只验证检索排序，不验证真实 LLM 答案质量、工具选择或拒答能力。生产默认 Hybrid 路径没有启用 Reranker，Multi-View 也没有参与本轮。

## 实验二：Multi-View Supplement + BGE Reranker

日期：2026-11-03  
状态：已完成，Multi-View 仍未接入生产默认路径。

实验流程：

```text
BGE-M3 Dense + BM25Plus + RRF
        ↓
固定原始 Hybrid Top 20
        +
Question View Dense 命中的新 Child（最多补充 20 个）
        ↓
BAAI/bge-reranker-v2-m3
        ↓
最终 Top 5
```

实验二没有重新对原始 Hybrid 排名做 View RRF。View 命中先映射回 canonical Child，并排除已经出现在原始 Hybrid Top 20 中的 Child。最终提供给 Reranker 和后续 LLM 的仍然是原始 Child 内容。

完整结果目录：
`evaluation_results/reranker_multiview_supplement_2026-11-02_v2/`。

复现命令：

```powershell
$env:HF_HUB_OFFLINE="1"
$env:TRANSFORMERS_OFFLINE="1"
.venv\Scripts\python.exe scripts/run_reranker_multiview_supplement_experiment.py `
  --offline `
  --output-dir evaluation_results/reranker_multiview_supplement_2026-11-02_v2
```

结果：

| 方案 | Parent Recall@5 | Parent Recall@10 | Parent MRR@5 | Parent NDCG@5 | P50 ms |
| --- | ---: | ---: | ---: | ---: | ---: |
| B：Hybrid Top 20 → Reranker | 96.94% | 98.89% | 92.26% | 93.33% | 8706.69 |
| C：Hybrid + Multi-View Supplement → Reranker | 96.39% | 98.89% | 91.98% | 92.84% | 16394.55 |
| 变化 | -0.55 个百分点 | 0.00 个百分点 | -0.28 个百分点 | -0.49 个百分点 | +7687.86 |

中文问题 → 英文文档：

| 方案 | Recall@5 | Recall@10 | MRR@5 | NDCG@5 |
| --- | ---: | ---: | ---: | ---: |
| B | 92.95% | 97.44% | 83.42% | 85.94% |
| C | 91.67% | 97.44% | 83.42% | 85.33% |

关键观察：

- 100 题全部完成，查询错误为 0；不可回答题仍不计入普通排序指标。
- 每题平均补充 18 个 Child，最多 20 个。
- 对 90 道可回答题逐题检查，补充候选中没有命中新的 Ground Truth Evidence；因此没有产生真正的召回收益。
- `rag_097` 的 Parent Recall@5 从 1.0 降到 0.5，是本轮唯一的 Recall@5 退步题；`rag_014` 的 Recall 不变，但 MRR/NDCG 下降。
- C 的额外候选主要是无关邻居，增加了 Reranker 计算量，并把部分原本已在候选池中的正确 Child 挤到 Top 5 之后。

结论：当前 Question View 质量和补充策略不足以参与 Reranker 候选池。Multi-View 应继续保留为独立实验能力；在没有“补充候选确实包含原始 Hybrid 未找到的正确证据”的证据前，不应开放给生产 Tool 调用。

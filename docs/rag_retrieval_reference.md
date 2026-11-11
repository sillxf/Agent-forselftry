# 本次 RAG 开发参考基准

后续改进可以直接与 2026-11-01 的真实运行比较，不需要重新走此前那一轮逐题人工审批。
此前署名审核的当前记录、批准状态和专用校验测试已撤销；当前数据恢复为审核前版本。
原始运行快照中的旧状态仅是当时输入的历史记录，不代表现在仍然批准。对照页面已去掉这些状态。

## 固定口径

- 30 个原问题：25 道可回答题，5 道不可回答题。
- 9 份固定文档，Hybrid（Dense + BM25 + RRF），Top-K=3。
- 排名单位是接口返回的 **去重 Parent 片段**，不是 Child 排名。
- 原始结果、提示及生成文本保持不变；撤销审核状态不影响检索评分。

| 指标 | 本次值 | 含义 |
| --- | ---: | --- |
| 正向题完整证据覆盖率 | **23/25 = 92%** | 一题所需的所有正向标注事实都被返回 |
| 宏平均 Evidence Recall@3 | **92%** | 先算每道可答题的事实召回率，再对 25 题平均 |
| 微平均事实召回率 | **37/43 ≈ 86.05%** | 按题统计的命中事实项数 / 所需事实项数 |
| 未完整召回的问题 | 011、014 | 本次这两题都没有命中正向标注事实 |
| 不可答题实际表现 | 5 道均输出资料不足或无法确定 | 本次这 5 题符合缺证据时不编造具体事实的预期；不代表其他未知题都能拒答 |
| 最终答案正确率 | **未统一评分** | 不能由上面的召回率代替 |

本次没有部分召回题，所以“完整证据覆盖率”和“宏平均 Recall”恰好同为 92%；以后出现部分召回时二者可能不同。
5 道不可答题不计入正向 Recall 的分母，不能把它们当成 5 次成功召回来提高分数。
机器可读的口径、参数和校验值在
[`retrieval_reference.json`](../evaluation_results/baselines/2026-11-01_http_answer_review_candidate_v2/retrieval_reference.json)。

## 必须分别跟踪的问题

1. **011：检索偏题且错用另一份清单作答。** 不只是格式问题。
2. **014：未召回预防措施，导致回答缺失。** 是检索效果问题。
3. **020：证据已召回，但生成模型拒绝回答。** 是生成/服务行为问题，不能用提升 Recall 掩盖。

实际答案与参考答案的差异直接保留在
[`review.html`](../evaluation_results/baselines/2026-11-01_http_answer_review_candidate_v2/review.html) 和
[`review.md`](../evaluation_results/baselines/2026-11-01_http_answer_review_candidate_v2/review.md)。

## 后续怎么比较

```powershell
.\.venv\Scripts\python.exe scripts/run_rag_answer_review.py --offline-models --generate --top-k 3 `
  --output-dir evaluation_results/next-http-answer-review
```

每次使用新的输出目录；脚本会保存新的 `retrieval_reference.json`。
比较前确认问题、参考答案、证据标注、语料以及 Top-K 和 Parent 计分口径一致。
`evaluation_definition_sha256` 排除审核人和审批状态，避免仅撤销审核就被误认为题目内容变化。
可以单变量改变 Embedding、切分或检索策略，但要记录清楚；不要把改 Top-K 后的分数直接当作同条件提升。
若修正参考答案、证据标注或更换文档，应对旧输出重新计分或重跑配对基准，不能硬拿旧的 92% 比较。

这是一个小型开发参考集，不是已充分验证的最终验收集，也不是一般安全问答准确率。
通用 `--require-reviewed` 严格门禁仍保留给未来正式验收；日常开发对比不使用该参数，不会被逐题审批阻塞。

## 实现位置

当前评测实现位于 `evaluation/rag/`，生产实现仍在 `app/rag/`；
`scripts/run_rag_answer_review.py` 仅作为命令入口。目录迁移不改变这份参考结果或评分口径。

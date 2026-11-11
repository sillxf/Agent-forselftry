# dual_dense_en_bm25_rrf retrieval baseline

Status: **provisional**; 100 labels pending human review.
Dataset: `security-rag-benchmark-v1-100-candidate-r2` / `0d1c86f478883b3b385e01828f5fddc9ac37f6df44e7bcc955fc88bca4ef37e3`.
Code: `289306494566fd379ad8b50b0b339e4f61baf89e`; dirty=True; source SHA-256 `8e9bc9a611e7f9d8410f72fb73964e555373b0ac404e9690799fb9d0c2ccf39c`.

Questions: 100; answerable: 90; unanswerable: 10.

| Ranking unit (K=5) | Evidence Recall | Result Precision | MRR | Result NDCG |
| --- | ---: | ---: | ---: | ---: |
| child | 0.9556 | 0.2267 | 0.8819 | 0.8944 |
| parent | 0.9889 | 0.2111 | 0.9174 | 0.9354 |

Child K and unique-parent K are different ranking units; do not combine them.
Metric contract: `result-qrels-v2`. Recall covers unique required facts; alternatives are OR locations.
Precision is relevant result slots / fixed K. Multiple distinct results supporting one fact remain relevant.
DCG uses max fact grade per result, gain 2^grade-1 and log2(rank+1) discount.
IDCG uses the sorted grades of ALL indexed units of the same type, not the number of facts.
Qrels are deterministically derived from body quotes and source IDs, not independently human-judged chunks.
Misses keep their rank. Metadata-only answers are not credited as body evidence.
Old v0.1 novelty/evidence metrics used a different definition and are not directly comparable.
No search, embedding, chunking or RRF change is implied by an evaluation score change.

## Categories

| Category | Questions | Child Recall | Child MRR | Parent Recall |
| --- | ---: | ---: | ---: | ---: |
| context | 5 | 1.0000 | 1.0000 | 1.0000 |
| exact_identifier | 5 | 0.8000 | 0.5667 | 1.0000 |
| mixed_terms | 13 | 1.0000 | 0.9231 | 1.0000 |
| multi_document | 5 | 1.0000 | 1.0000 | 1.0000 |
| paraphrase | 8 | 1.0000 | 0.9000 | 1.0000 |
| response | 5 | 1.0000 | 1.0000 | 1.0000 |
| semantic | 5 | 0.8000 | 0.7000 | 0.8000 |
| tables_steps | 5 | 1.0000 | 0.9000 | 1.0000 |
| technique_confusion | 15 | 0.9333 | 0.9000 | 1.0000 |
| unanswerable | 10 | N/A | N/A | N/A |
| zh_to_en | 24 | 0.9583 | 0.8681 | 1.0000 |

## Engineering diagnostics

Errors: 0; no-result rate: 0.0000.
Retrieval latency ms (mean/P50/P95): 359.74 / 414.07 / 503.27.
Latency excludes model/index setup and evidence scoring. The first query is not warmed separately.
Mean parent context length: 13769.6 characters.
This is a size diagnostic, not a validated context-noise/precision metric.
Unanswerable cases are excluded from ranking averages; no refusal rate is inferred.

## Failures

- `rag_001`: first_result_not_relevant — T1059.001 refers to which Windows scripting environment?
- `rag_003`: first_result_not_relevant — Which ATT&CK technique name corresponds to T1078?
- `rag_004`: no_relevant_child, first_result_not_relevant — Which OWASP WSTG test identifier covers SQL injection?
- `rag_007`: first_result_not_relevant — Can password guessing be performed without contacting a live authentication service?
- `rag_009`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — How can a tester infer database information when no data is returned directly?
- `rag_020`: first_result_not_relevant — When enumerating SQL-injection inputs, should hidden POST fields, HTTP headers and cookies be included?
- `rag_031`: first_result_not_relevant — 为什么取证时没有发现新落地的程序文件，也不能排除系统自带脚本环境曾下载并运行过程序？
- `rag_037`: first_result_not_relevant — 某个站点泄露的成对用户名和口令，为什么会被攻击者带到另一个站点再试一次？
- `rag_043`: first_result_not_relevant — 办公文档为什么能像小程序一样，在事件触发时自动执行主机任务？
- `rag_046`: first_result_not_relevant — 攻击者借用合法账号连接远程管理机制后，会以哪个登录身份执行后续操作？
- `rag_049`: no_relevant_child, first_result_not_relevant — 数据库结果不直接出现在页面中时，测试者可以通过什么观察方式重建信息？
- `rag_056`: first_result_not_relevant — VBA macro 为什么能让 Office 文档自动执行宿主机上的任务？
- `rag_059`: first_result_not_relevant — WinRM 不只是 PowerShell 命令名，它在系统里同时代表哪两种东西？
- `rag_074`: first_result_not_relevant — 不去猜用户的口令，而是寻找已经登录的会话留下的秘密，应查看哪里，又需要哪类身份才能提取？
- `rag_077`: first_result_not_relevant — 攻击者已经拿到外站泄露的成对账号密码，再利用用户复用习惯登录目标；这与轮试常见口令的模式如何区分？
- `rag_088`: no_relevant_child, first_result_not_relevant — Which retrieval method reconstructs information from database behaviour without receiving it through another channel?

## Scope and limitations

All source evidence and quotes were checked against the actual index before evaluation.
Pending labels are AI-prepared candidates, not human-certified ground truth. Review alternative
valid sources, grades and unanswerable rationales before treating these scores as acceptance results.
This small development set is not a holdout benchmark and does not establish general accuracy.
No LLM answer generation, judge, reranker, production embedding migration or automatic tuning was performed.
Read `retrieval_results.jsonl` and `failures.json` for full ranks, scores, quotes and provenance.

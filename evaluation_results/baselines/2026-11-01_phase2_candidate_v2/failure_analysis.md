# 失败定位（不修改题目或检索设置）

所有分类基于源引用、完整索引、原始 Top K 和相同候选池；原因推断不是已证实的模型缺陷。

## 分类统计（题目 × 策略，可多分类）

- Lexical Mismatch: 1
- Semantic Mismatch: 0
- Cross-lingual Retrieval Failure: 6
- Chunk Boundary Problem: 0
- Parent Recovery Problem: 0
- Metadata / Structure Problem: 0
- Ranking Problem: 21
- Evidence Annotation Problem: 0

## 失败案例

### rag_001 / dense

T1059.001 refers to which Windows scripting environment?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_002 / dense

What technique is assigned the ATT&CK identifier T1110?
- 分类：Ranking Problem
- 正确候选首次排名：4
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=4; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_003 / dense

Which ATT&CK technique name corresponds to T1078?
- 分类：Ranking Problem
- 正确候选首次排名：3
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=3; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_004 / dense

Which OWASP WSTG test identifier covers SQL injection?
- 分类：Ranking Problem
- 正确候选首次排名：13
- Child Top K 缺少事实：['owasp_wstg_v4_2_sql_injection-b1-1']
- 原因：First relevant configured-pool candidate rank=13; missing Top-K facts=['owasp_wstg_v4_2_sql_injection-b1-1'].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_009 / dense

How can a tester infer database information when no data is returned directly?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_011 / dense

暴力破解告警的本地响应清单建议采取哪些措施？
- 分类：Cross-lingual Retrieval Failure
- 正确候选首次排名：None
- Child Top K 缺少事实：['brute_force-b10-1', 'brute_force-b11-2', 'brute_force-b12-3']
- 原因：Relevant indexed evidence did not enter the configured candidate pool; language/wording is a hypothesis, not proof.
- 建议：Use the separate original/translated/multilingual/dual-route experiment, keeping original queries unchanged.

### rag_014 / dense

本地 SQL 注入知识库列出了哪些预防措施？
- 分类：Cross-lingual Retrieval Failure
- 正确候选首次排名：None
- Child Top K 缺少事实：['sql_injection-b10-2', 'sql_injection-b11-3', 'sql_injection-b9-1']
- 原因：Relevant indexed evidence did not enter the configured candidate pool; language/wording is a hypothesis, not proof.
- 建议：Use the separate original/translated/multilingual/dual-route experiment, keeping original queries unchanged.

### rag_016 / dense

For detection rule R004, what severity and response are specified?
- 分类：Ranking Problem
- 正确候选首次排名：4
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=4; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_018 / dense

What are the three numbered actions in the response checklist, in order?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_020 / dense

When enumerating SQL-injection inputs, should hidden POST fields, HTTP headers and cookies be included?
- 分类：Ranking Problem
- 正确候选首次排名：8
- Child Top K 缺少事实：['owasp_wstg_v4_2_sql_injection-b34-1']
- 原因：First relevant configured-pool candidate rank=8; missing Top-K facts=['owasp_wstg_v4_2_sql_injection-b34-1'].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_024 / dense

What cross-account authentication indicators and matching response actions are listed in the brute-force guide?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_002 / bm25

What technique is assigned the ATT&CK identifier T1110?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_003 / bm25

Which ATT&CK technique name corresponds to T1078?
- 分类：Ranking Problem
- 正确候选首次排名：3
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=3; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_004 / bm25

Which OWASP WSTG test identifier covers SQL injection?
- 分类：Lexical Mismatch
- 正确候选首次排名：None
- Child Top K 缺少事实：['owasp_wstg_v4_2_sql_injection-b1-1']
- 原因：Relevant indexed evidence did not enter the configured candidate pool; language/wording is a hypothesis, not proof.
- 建议：Use the separate original/translated/multilingual/dual-route experiment, keeping original queries unchanged.

### rag_005 / bm25

检测规则 R002 的严重程度和响应动作是什么？
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_007 / bm25

Can password guessing be performed without contacting a live authentication service?
- 分类：Ranking Problem
- 正确候选首次排名：4
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=4; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_009 / bm25

How can a tester infer database information when no data is returned directly?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_011 / bm25

暴力破解告警的本地响应清单建议采取哪些措施？
- 分类：Cross-lingual Retrieval Failure
- 正确候选首次排名：None
- Child Top K 缺少事实：['brute_force-b10-1', 'brute_force-b11-2', 'brute_force-b12-3']
- 原因：Relevant indexed evidence did not enter the configured candidate pool; language/wording is a hypothesis, not proof.
- 建议：Use the separate original/translated/multilingual/dual-route experiment, keeping original queries unchanged.

### rag_014 / bm25

本地 SQL 注入知识库列出了哪些预防措施？
- 分类：Cross-lingual Retrieval Failure
- 正确候选首次排名：None
- Child Top K 缺少事实：['sql_injection-b10-2', 'sql_injection-b11-3', 'sql_injection-b9-1']
- 原因：Relevant indexed evidence did not enter the configured candidate pool; language/wording is a hypothesis, not proof.
- 建议：Use the separate original/translated/multilingual/dual-route experiment, keeping original queries unchanged.

### rag_018 / bm25

What are the three numbered actions in the response checklist, in order?
- 分类：Ranking Problem
- 正确候选首次排名：5
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=5; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_022 / bm25

Why does NIST Rev. 3 emphasize cybersecurity risk management instead of maintaining every detailed response procedure?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_024 / bm25

What cross-account authentication indicators and matching response actions are listed in the brute-force guide?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_002 / hybrid

What technique is assigned the ATT&CK identifier T1110?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_003 / hybrid

Which ATT&CK technique name corresponds to T1078?
- 分类：Ranking Problem
- 正确候选首次排名：3
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=3; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_004 / hybrid

Which OWASP WSTG test identifier covers SQL injection?
- 分类：Ranking Problem
- 正确候选首次排名：26
- Child Top K 缺少事实：['owasp_wstg_v4_2_sql_injection-b1-1']
- 原因：First relevant configured-pool candidate rank=26; missing Top-K facts=['owasp_wstg_v4_2_sql_injection-b1-1'].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

### rag_011 / hybrid

暴力破解告警的本地响应清单建议采取哪些措施？
- 分类：Cross-lingual Retrieval Failure
- 正确候选首次排名：None
- Child Top K 缺少事实：['brute_force-b10-1', 'brute_force-b11-2', 'brute_force-b12-3']
- 原因：Relevant indexed evidence did not enter the configured candidate pool; language/wording is a hypothesis, not proof.
- 建议：Use the separate original/translated/multilingual/dual-route experiment, keeping original queries unchanged.

### rag_014 / hybrid

本地 SQL 注入知识库列出了哪些预防措施？
- 分类：Cross-lingual Retrieval Failure
- 正确候选首次排名：None
- Child Top K 缺少事实：['sql_injection-b10-2', 'sql_injection-b11-3', 'sql_injection-b9-1']
- 原因：Relevant indexed evidence did not enter the configured candidate pool; language/wording is a hypothesis, not proof.
- 建议：Use the separate original/translated/multilingual/dual-route experiment, keeping original queries unchanged.

### rag_016 / hybrid

For detection rule R004, what severity and response are specified?
- 分类：Ranking Problem
- 正确候选首次排名：2
- Child Top K 缺少事实：[]
- 原因：First relevant configured-pool candidate rank=2; missing Top-K facts=[].
- 建议：Inspect candidate ordering and source context; do not assume a reranker helps.

## 不可回答题

15 条题目×策略记录保留了真实邻近结果；不能据此声称 Agent 能拒答或检测知识缺口。
查看 unanswerable_analysis.json 和后续 Agent Evaluation 设计。

完整 Chunk、来源、Block ID、候选排名和必要事实见 JSON；与历史标签错误分开记录。

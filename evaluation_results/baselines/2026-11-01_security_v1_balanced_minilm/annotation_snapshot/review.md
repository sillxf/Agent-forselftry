# Security V1 Ground Truth 审核清单

全部状态来自 JSONL；AI 校验不能勾选人工通过。id 对应 question_id；relevant_evidence[].evidence_id 对应 evidence_ids。

- [ ] 问题可由引用完整回答，不依赖标题猜测、未给出的日志或因果推断。
- [ ] 核对全部必要事实、等价替代位置和多文档依赖。
- [ ] 核对自然中文/术语/英文翻译是否语义一致，没有漏条件或添加答案。
- [ ] 确认干扰来源确实相似但不能满足本问题要求。
- [ ] 知识缺口题已确认在整套冻结资料中不存在答案。

## rag_001 — english

T1059.001 refers to which Windows scripting environment?

参考答案：PowerShell.
语言：en → en；主题：execution；难度：easy
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_001
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b1-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell；页 None–None
  - 原文：T1059.001: PowerShell
  - Block IDs：c2440acc-92b4-55a1-8358-fc947f7295d9；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_002 — english

What technique is assigned the ATT&CK identifier T1110?

参考答案：Brute Force.
语言：en → en；主题：authentication；难度：easy
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_002
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b20-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1110: Brute Force；页 None–None
  - 原文：T1110: Brute Force
  - Block IDs：a48dc3aa-8f9c-5c85-b374-1f7e73d0822a；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_003 — english

Which ATT&CK technique name corresponds to T1078?

参考答案：Valid Accounts.
语言：en → en；主题：account_abuse；难度：easy
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_003
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b33-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts；页 None–None
  - 原文：T1078: Valid Accounts
  - Block IDs：ff189459-e060-5175-9606-305270c8b3e2；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_004 — english

Which OWASP WSTG test identifier covers SQL injection?

参考答案：WSTG-INPV-05.
语言：en → en；主题：sql_injection；难度：easy
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_004
干扰来源：未指定专用干扰源；仍检索完整语料

- `owasp_wstg_v4_2_sql_injection-b1-1` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection；页 None–None
  - 原文：ID: WSTG-INPV-05
  - Block IDs：5e57aec8-0467-56af-ae82-5d6a0ddc5fb1；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_005 — mixed_terms

检测规则 R002 的严重程度和响应动作是什么？

参考答案：Critical；Isolate。
语言：mixed → en；主题：detection_rules；难度：easy
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_005
干扰来源：未指定专用干扰源；仍检索完整语料

- `continued_rules-r002` — continued_rules.pdf；章节 Detection Rules；页 1–2
  - 原文：Rule ID: R002
Severity: Critical
Response: Isolate
  - Block IDs：0a3d43db-7507-5175-932e-b0e4c63d7cc4, 23a74a07-c821-5432-9917-c1bcab1862ff；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_006 — paraphrase

Can the Windows scripting shell fetch an executable and run it without first writing it to disk?

参考答案：Yes; PowerShell can download executables and execute them in memory.
语言：en → en；主题：execution；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_006
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b7-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell；页 None–None
  - 原文：PowerShell may also be used to download and run executables from the Internet, which can be executed from disk or in memory without touching disk.
  - Block IDs：33fd520c-129b-5f4b-8df8-a97aacf70b18；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_007 — paraphrase

Can password guessing be performed without contacting a live authentication service?

参考答案：Yes; brute forcing can run offline against acquired credential data such as password hashes.
语言：en → en；主题：credential_access；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_007
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b21-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1110: Brute Force；页 None–None
  - 原文：offline against previously acquired credential data, such as password hashes.
  - Block IDs：4d51492c-82c9-5070-bbb3-9fdb5fbfde4f；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_008 — paraphrase

Why might an intruder reuse an employee account that is no longer active?

参考答案：The original user is absent and cannot notice anomalous account activity.
语言：en → en；主题：account_abuse；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_008
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b35-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts；页 None–None
  - 原文：the original account user will not be present to identify any anomalous activity taking place on their account.
  - Block IDs：bb628f12-2e55-5087-9388-86597c2be15c；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_009 — paraphrase

How can a tester infer database information when no data is returned directly?

参考答案：Use inferential/blind SQL injection: send requests and observe database behaviour.
语言：en → en；主题：sql_injection；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_009
干扰来源：未指定专用干扰源；仍检索完整语料

- `owasp_wstg_v4_2_sql_injection-b17-1` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > Summary；页 None–None
  - 原文：Inferential or Blind: there is no actual transfer of data, but the tester is able to reconstruct the information by sending particular requests and observing the resulting behavior of the DB Server.
  - Block IDs：43da13f1-0522-5462-9973-325458b7c9e8；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_010 — english

What kinds of observable occurrences are considered events in the NIST incident-response guidance?

参考答案：Observable occurrences involving computing assets, including platforms, networks, services and cloud environments.
语言：en → en；主题：incident_response；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_010
干扰来源：未指定专用干扰源；仍检索完整语料

- `nist_sp80061r3_pp10-12-b1-1` — nist_sp80061r3_pp10-12.pdf；章节 1. Introduction；页 1–1
  - 原文：Within this document, an event is any observable occurrence that involves computing assets, including physical and virtual platforms, networks, services, and cloud environments.
  - Block IDs：ff45e0e6-d8a0-516a-9adf-527fecaebd31；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_011 — zh_to_en

暴力破解告警的本地响应清单建议采取哪些措施？

参考答案：封禁可疑 IP、启用 MFA、调查受影响账户。
语言：zh → en；主题：authentication；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_011
干扰来源：未指定专用干扰源；仍检索完整语料

- `brute_force-b10-1` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Block suspicious IP
  - Block IDs：c74f8193-1c4e-505f-8635-a2ee3765eb35；同义位置 0 个
- `brute_force-b11-2` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Enable MFA
  - Block IDs：e4c5acd1-6a01-5eb2-b76f-921c176f8483；同义位置 0 个
- `brute_force-b12-3` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Investigate affected accounts
  - Block IDs：fdc90658-40c0-5122-b255-1b934a93812b；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_012 — english

According to the malware response checklist, how should compromised credentials and backups be handled?

参考答案：Reset compromised credentials and restore systems from clean backups.
语言：en → en；主题：incident_response；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_012
干扰来源：未指定专用干扰源；仍检索完整语料

- `malware-b17-1` — malware.md；章节 Malware > Response；页 None–None
  - 原文：Reset compromised credentials
  - Block IDs：cddc7cd0-ca46-5b71-9ce2-04c512eba076；同义位置 0 个
- `malware-b18-2` — malware.md；章节 Malware > Response；页 None–None
  - 原文：Restore systems from clean backups
  - Block IDs：192826d3-d01b-531a-b2f0-c19e1f69f940；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_013 — english

What immediate network containment action does the malware response checklist recommend?

参考答案：Isolate affected systems from the network.
语言：en → en；主题：incident_response；难度：easy
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_013
干扰来源：未指定专用干扰源；仍检索完整语料

- `malware-b14-1` — malware.md；章节 Malware > Response；页 None–None
  - 原文：Isolate affected systems from the network
  - Block IDs：673d2578-1560-51e1-a55a-1323de1d3798；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_014 — mixed_terms

本地 SQL 注入知识库列出了哪些预防措施？

参考答案：预编译语句、输入验证、最小权限。
语言：mixed → en；主题：sql_injection；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_014
干扰来源：未指定专用干扰源；仍检索完整语料

- `sql_injection-b9-1` — sql_injection.md；章节 SQL Injection > Prevention；页 None–None
  - 原文：Prepared statements
  - Block IDs：e13ebf1a-556b-55b7-9bf3-e89f062b4bf6；同义位置 0 个
- `sql_injection-b10-2` — sql_injection.md；章节 SQL Injection > Prevention；页 None–None
  - 原文：Input validation
  - Block IDs：4dfe812d-d459-533d-ae8a-6066c26ecc95；同义位置 0 个
- `sql_injection-b11-3` — sql_injection.md；章节 SQL Injection > Prevention；页 None–None
  - 原文：Least privilege
  - Block IDs：0c38339f-b554-59f9-a5cd-c230f13ef0d7；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_015 — paraphrase

Why should lessons learned during incident response be shared before recovery has finished?

参考答案：Modern incidents are frequent, complex and lengthy; lessons should be shared as identified to support continuous improvement.
语言：en → en；主题：incident_response；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_015
干扰来源：未指定专用干扰源；仍检索完整语料

- `nist_sp80061r3_pp10-12-b38-1` — nist_sp80061r3_pp10-12.pdf；章节 2. Incident Response as Part of Cybersecurity Risk Management > 2.1. Incident Response Life Cycle Model；页 3–3
  - 原文：The lessons learned during incident response should often be shared as soon as they are identified, not delayed until after recovery concludes.
  - Block IDs：f6162960-05d9-52ae-9d47-a71be9bf79ae；同义位置 0 个
- `nist-modern-incident-complexity` — nist_sp80061r3_pp10-12.pdf；章节 2. Incident Response as Part of Cybersecurity Risk Management > 2.1. Incident Response Life Cycle Model；页 3–3
  - 原文：Today, incidents occur frequently and cause far more damage. Recovering from them often takes weeks or months due to their breadth, complexity, and dynamic nature.
  - Block IDs：f6162960-05d9-52ae-9d47-a71be9bf79ae；同义位置 0 个
- `nist-continuous-improvement` — nist_sp80061r3_pp10-12.pdf；章节 2. Incident Response as Part of Cybersecurity Risk Management > 2.1. Incident Response Life Cycle Model；页 3–3
  - 原文：Continuous improvement is increasingly necessary for all facets of cybersecurity risk management in order to keep up with modern threats.
  - Block IDs：f6162960-05d9-52ae-9d47-a71be9bf79ae；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_016 — english

For detection rule R004, what severity and response are specified?

参考答案：High; Block.
语言：en → en；主题：detection_rules；难度：easy
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_016
干扰来源：未指定专用干扰源；仍检索完整语料

- `continued_rules-r004` — continued_rules.pdf；章节 Detection Rules；页 1–2
  - 原文：Rule ID: R004
Severity: High
Response: Block
  - Block IDs：0a3d43db-7507-5175-932e-b0e4c63d7cc4, 23a74a07-c821-5432-9917-c1bcab1862ff；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_017 — english

Which rule has Medium severity and what response does it require?

参考答案：R003; Review.
语言：en → en；主题：detection_rules；难度：easy
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_017
干扰来源：未指定专用干扰源；仍检索完整语料

- `continued_rules-r003` — continued_rules.pdf；章节 Detection Rules；页 1–2
  - 原文：Rule ID: R003
Severity: Medium
Response: Review
  - Block IDs：0a3d43db-7507-5175-932e-b0e4c63d7cc4, 23a74a07-c821-5432-9917-c1bcab1862ff；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_018 — english

What are the three numbered actions in the response checklist, in order?

参考答案：Check firewall configuration; collect authentication logs; isolate affected hosts.
语言：en → mixed；主题：incident_response；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_018
干扰来源：未指定专用干扰源；仍检索完整语料

- `numbered_steps-b1-1` — numbered_steps.docx；章节 Response checklist；页 None–None
  - 原文：1. Check firewall configuration
  - Block IDs：34337ceb-b993-5c48-af5a-98498100cf5a；同义位置 1 个
- `numbered_steps-b2-2` — numbered_steps.docx；章节 Response checklist；页 None–None
  - 原文：2. Collect authentication logs
  - Block IDs：aec40a56-e98b-5dcf-943a-e3c9512395d8；同义位置 1 个
- `numbered_steps-b3-3` — numbered_steps.docx；章节 Response checklist；页 None–None
  - 原文：3. Isolate affected hosts
  - Block IDs：4c284a64-54ca-5487-a6c4-5d69aa0e3c81；同义位置 1 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_019 — english

What does the authentication rule do after checking events in the cross-page investigation note?

参考答案：It correlates failed login attempts across accounts.
语言：en → en；主题：authentication；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_019
干扰来源：未指定专用干扰源；仍检索完整语料

- `sentence_continuation-b1-1` — sentence_continuation.pdf；章节 Authentication investigation；页 1–2
  - 原文：The authentication rule checks events, then correlates failed login attempts across accounts.
  - Block IDs：a29b1520-dbe7-59b7-8f00-c089f5767197；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_020 — english

When enumerating SQL-injection inputs, should hidden POST fields, HTTP headers and cookies be included?

参考答案：Yes; test the input fields separately and consider headers and cookies.
语言：en → en；主题：sql_injection；难度：medium
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_020
干扰来源：未指定专用干扰源；仍检索完整语料

- `owasp_wstg_v4_2_sql_injection-b34-1` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > How to Test > Detection Techniques；页 None–None
  - 原文：The tester has to make a list of all input fields whose values could be used in crafting a SQL query, including the hidden fields of POST requests and then test them separately, trying to interfere with the query and to generate an error. Consider also HTTP headers and Cookies.
  - Block IDs：2a3b25de-590d-55a4-a251-2cfef4274def；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_021 — english

How do inband, out-of-band and blind SQL injection differ in the way information is obtained?

参考答案：Inband uses the injection channel; out-of-band uses another channel; blind infers from behaviour without direct data transfer.
语言：en → en；主题：sql_injection；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_021
干扰来源：未指定专用干扰源；仍检索完整语料

- `owasp_wstg_v4_2_sql_injection-b15-1` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > Summary；页 None–None
  - 原文：Inband: data is extracted using the same channel that is used to inject the SQL code.
  - Block IDs：ca6280cf-0816-550f-8857-089ee53e158d；同义位置 0 个
- `owasp_wstg_v4_2_sql_injection-b16-2` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > Summary；页 None–None
  - 原文：Out-of-band: data is retrieved using a different channel
  - Block IDs：f2a22a75-f5e5-51f3-a548-4d7639e958b8；同义位置 1 个
- `owasp_wstg_v4_2_sql_injection-b17-3` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > Summary；页 None–None
  - 原文：Inferential or Blind: there is no actual transfer of data, but the tester is able to reconstruct the information by sending particular requests and observing the resulting behavior of the DB Server.
  - Block IDs：43da13f1-0522-5462-9973-325458b7c9e8；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_022 — english

Why does NIST Rev. 3 emphasize cybersecurity risk management instead of maintaining every detailed response procedure?

参考答案：Detailed procedures vary and change too often for one static publication; the revision focuses on all CSF 2.0 Functions.
语言：en → en；主题：incident_response；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_022
干扰来源：未指定专用干扰源；仍检索完整语料

- `nist_sp80061r3_pp10-12-b14-1` — nist_sp80061r3_pp10-12.pdf；章节 1. Introduction > 1.1. Purpose and Scope；页 2–2
  - 原文：Because the details of how to perform incident response activities change so often and vary so much across technologies, environments, and organizations, it is no longer feasible to capture and maintain that information in a single static publication.
  - Block IDs：4a0e88f0-2723-5bcc-83f6-e62e853990cc；同义位置 0 个
- `nist_sp80061r3_pp10-12-b14-2` — nist_sp80061r3_pp10-12.pdf；章节 1. Introduction > 1.1. Purpose and Scope；页 2–2
  - 原文：this version focuses on improving cybersecurity risk management for all of the NIST Cybersecurity Framework (CSF) 2.0 Functions
  - Block IDs：4a0e88f0-2723-5bcc-83f6-e62e853990cc；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_023 — english

For remote PowerShell command execution, which cmdlet is mentioned and what permission prerequisite applies?

参考答案：Invoke-Command; administrator permissions are required to connect to remote systems.
语言：en → en；主题：remote_execution；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_023
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b5-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell；页 None–None
  - 原文：Invoke-Command
  - Block IDs：a3d32a81-9c33-58d7-bb87-3e48ded23c83；同义位置 0 个
- `mitre_attack_v17_1-b6-2` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell；页 None–None
  - 原文：administrator permissions are required to use PowerShell to connect to remote systems
  - Block IDs：05d2351c-251b-5dc8-9104-11f43821c958；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_024 — paraphrase

What cross-account authentication indicators and matching response actions are listed in the brute-force guide?

参考答案：Same source IP attacking multiple accounts/high-frequency failures; block suspicious IP, enable MFA and investigate accounts.
语言：en → en；主题：authentication；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_024
干扰来源：未指定专用干扰源；仍检索完整语料

- `brute_force-b6-1` — brute_force.md；章节 Brute Force Attack > Detection；页 None–None
  - 原文：Same source IP attacking multiple accounts
  - Block IDs：efffc5d5-51e8-5756-bb79-b4c0dfc8bc6b；同义位置 0 个
- `brute_force-b7-2` — brute_force.md；章节 Brute Force Attack > Detection；页 None–None
  - 原文：High frequency authentication failures
  - Block IDs：6423c98c-3b78-50dc-9d12-d5d4dad460e9；同义位置 0 个
- `brute_force-b10-3` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Block suspicious IP
  - Block IDs：c74f8193-1c4e-505f-8635-a2ee3765eb35；同义位置 0 个
- `brute_force-b11-4` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Enable MFA
  - Block IDs：e4c5acd1-6a01-5eb2-b76f-921c176f8483；同义位置 0 个
- `brute_force-b12-5` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Investigate affected accounts
  - Block IDs：fdc90658-40c0-5122-b255-1b934a93812b；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_025 — paraphrase

What does the valid-accounts description say about both bypassing access controls and moving across account types?

参考答案：Compromised credentials can bypass controls; overlapping local, domain and cloud permissions can enable privilege escalation.
语言：en → en；主题：account_abuse；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_025
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b34-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts；页 None–None
  - 原文：Compromised credentials may be used to bypass access controls
  - Block IDs：9df49cee-b541-5e50-a1db-22159ec3bf17；同义位置 0 个
- `mitre_attack_v17_1-b36-2` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts；页 None–None
  - 原文：The overlap of permissions for local, domain, and cloud accounts across a network of systems is of concern because the adversary may be able to pivot across accounts and systems to reach a high level of access (i.e., domain or enterprise administrator) to bypass access controls set within the enterprise.
  - Block IDs：b96b8f17-37a3-5d39-b01e-c367ec19ce11；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_026 — unanswerable

What is the exact production API key for the fictional Acme SOC deployment?

参考答案：Insufficient evidence in this corpus.
语言：en → none；主题：knowledge_gap；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_026
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_027 — unanswerable

What indicators of compromise are documented for the fictional CVE-2099-99999?

参考答案：Insufficient evidence in this corpus.
语言：en → none；主题：knowledge_gap；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_027
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_028 — unanswerable

在 2026-10-31 这次告警中，攻击者实际登录了哪些生产账户？

参考答案：Insufficient evidence in this corpus.
语言：zh → none；主题：knowledge_gap；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_028
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_029 — unanswerable

Which vendor firmware command disables the fictional QuantumShield X900 audit engine?

参考答案：Insufficient evidence in this corpus.
语言：en → none；主题：knowledge_gap；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_029
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_030 — unanswerable

What exact financial loss did the fictional ACME incident cause on 2026-10-31?

参考答案：Insufficient evidence in this corpus.
语言：en → none；主题：knowledge_gap；难度：hard
状态：pending；审核人：未填写
设计说明：Inherited verbatim from the legacy 30-question candidate; this categorization is AI metadata, not human approval.
查询族：legacy-rag_030
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_031 — zh_to_en

为什么取证时没有发现新落地的程序文件，也不能排除系统自带脚本环境曾下载并运行过程序？

参考答案：PowerShell can download executables and run them in memory without touching disk.
语言：zh → en；主题：execution；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：ps-memory
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b7-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell；页 None–None
  - 原文：PowerShell may also be used to download and run executables from the Internet, which can be executed from disk or in memory without touching disk.
  - Block IDs：33fd520c-129b-5f4b-8df8-a97aacf70b18；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_032 — zh_to_en

用系统自带脚本环境连接另一台机器执行任务时，资料要求连接方具备什么权限？

参考答案：Administrator permissions are required for PowerShell connections to remote systems.
语言：zh → en；主题：remote_execution；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：ps-admin
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b6-2` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell；页 None–None
  - 原文：administrator permissions are required to use PowerShell to connect to remote systems
  - Block IDs：05d2351c-251b-5dc8-9104-11f43821c958；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_033 — zh_to_en

离职人员的身份被重新使用时，为什么这种活动可能更不容易被本人察觉？

参考答案：The original account user is absent and cannot notice anomalous activity.
语言：zh → en；主题：account_abuse；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：dormant
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b35-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts；页 None–None
  - 原文：the original account user will not be present to identify any anomalous activity taking place on their account.
  - Block IDs：bb628f12-2e55-5087-9388-86597c2be15c；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_034 — zh_to_en

攻击者已经拿到合法登录凭据时，还可能绕过资源上的哪类限制？

参考答案：Compromised credentials may bypass access controls.
语言：zh → en；主题：account_abuse；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：controls
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b34-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts；页 None–None
  - 原文：Compromised credentials may be used to bypass access controls
  - Block IDs：9df49cee-b541-5e50-a1db-22159ec3bf17；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_035 — zh_to_en

大量身份各只收到少数几个常见口令的尝试，这种横着铺开的登录行为属于什么模式？

参考答案：Password spraying uses one or a small list of common passwords against many accounts.
语言：zh → en；主题：authentication；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：spray-pattern
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-spray-pattern` — attack_t1110_003.md；章节 T1110.003: Password Spraying；页 None–None
  - 原文：Adversaries may use a single or small list of commonly used passwords against many different accounts to attempt to acquire valid account credentials.
  - Block IDs：56673f90-6e84-5f53-a039-486e18269926；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_036 — zh_to_en

把同一个候选口令轮流用于许多身份，而不是对单个身份反复更换口令，这样做是在规避什么？

参考答案：Account lockouts caused by many guesses against one account.
语言：zh → en；主题：authentication；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：spray-lockout
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-spray-lockout` — attack_t1110_003.md；章节 T1110.003: Password Spraying；页 None–None
  - 原文：Logins are attempted with that password against many different accounts on a network to avoid account lockouts that would normally occur when brute forcing a single account with many passwords.
  - Block IDs：56673f90-6e84-5f53-a039-486e18269926；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_037 — zh_to_en

某个站点泄露的成对用户名和口令，为什么会被攻击者带到另一个站点再试一次？

参考答案：Credential stuffing exploits overlap and users reusing passwords across personal and business accounts.
语言：zh → en；主题：authentication；难度：hard
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：stuffing-cause|stuffing-reuse
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-stuffing-reuse` — attack_t1110_004.md；章节 T1110.004: Credential Stuffing；页 None–None
  - 原文：Adversaries may use credentials obtained from breach dumps of unrelated accounts to gain access to target accounts through credential overlap.
  - Block IDs：998cc467-f643-58aa-938a-2e1e23e1c412；同义位置 0 个
- `security-v1-stuffing-cause` — attack_t1110_004.md；章节 T1110.004: Credential Stuffing；页 None–None
  - 原文：taking advantage of the tendency for users to use the same passwords across personal and business accounts.
  - Block IDs：998cc467-f643-58aa-938a-2e1e23e1c412；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_038 — zh_to_en

攻击者不认识用户实际输入的密码字符，却拿着窃取的摘要完成认证，这属于哪种做法？

参考答案：Pass the Hash authenticates as a user without the cleartext password.
语言：zh → en；主题：credential_access；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：pth-auth
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-pth-auth` — attack_t1550_002.md；章节 T1550.002: Pass the Hash；页 None–None
  - 原文：Pass the hash (PtH) is a method of authenticating as a user without having access to the user's cleartext password.
  - Block IDs：a7b92d0e-65b1-5b80-9e49-dd5014661713；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_039 — zh_to_en

用户已经在主机上登录后，系统哪个安全进程的内存会保存可被窃取的凭据材料？

参考答案：LSASS process memory stores credential materials after logon.
语言：zh → en；主题：credential_access；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：lsass-memory
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-lsass-memory` — attack_t1003_001.md；章节 T1003.001: LSASS Memory；页 None–None
  - 原文：After a user logs on, the system generates and stores a variety of credential materials in LSASS process memory.
  - Block IDs：fd740129-64cf-5f89-8c24-62cf6b963a07；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_040 — zh_to_en

攻击者把程序挂到用户登录时自动执行的位置，这个触发时机是什么？

参考答案：It executes when a user logs in.
语言：zh → en；主题：persistence；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：run-logon
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-run-logon` — attack_t1547_001.md；章节 T1547.001: Registry Run Keys / Startup Folder；页 None–None
  - 原文：Adding an entry to the "run keys" in the Registry or startup folder will cause the program referenced to be executed when a user logs in.
  - Block IDs：8463fc42-6ce3-59a2-9c2b-c2263af4c057；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_041 — zh_to_en

借助用户登录自启动位置运行的程序，通常继承谁的身份上下文和权限？

参考答案：The user context and associated account permissions.
语言：zh → en；主题：persistence；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：run-context
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-run-context` — attack_t1547_001.md；章节 T1547.001: Registry Run Keys / Startup Folder；页 None–None
  - 原文：These programs will be executed under the context of the user and will have the account's associated permissions level.
  - Block IDs：8463fc42-6ce3-59a2-9c2b-c2263af4c057；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_042 — zh_to_en

管理员希望把重复工作保存为可按顺序运行、还能写条件和循环的命令清单，哪种文件机制能做到？

参考答案：Windows command-shell batch files such as .bat or .cmd.
语言：zh → en；主题：execution；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：batch
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-batch` — attack_t1059_003.md；章节 T1059.003: Windows Command Shell；页 None–None
  - 原文：Batch files (ex: .bat or .cmd) also provide the shell with a list of sequential commands to run, as well as normal scripting operations such as conditionals and loops.
  - Block IDs：04113221-c298-563b-8678-db6e7818695e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_043 — zh_to_en

办公文档为什么能像小程序一样，在事件触发时自动执行主机任务？

参考答案：VBA is event-driven and lets Office documents contain task-automation macros.
语言：zh → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：vba-event|vba-macros
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-vba-event` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA is an event-driven programming language built into Microsoft Office, as well as several third-party applications.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- `security-v1-vba-macros` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA enables documents to contain macros used to automate the execution of tasks and other functionality on the host.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_044 — zh_to_en

一种常被当成网页专用的脚本语言，能否在没有浏览器页面的运行环境里执行？

参考答案：Yes; JavaScript can execute in runtime environments outside the browser.
语言：zh → en；主题：execution；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：js-runtime
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-js-runtime` — attack_t1059_007.md；章节 T1059.007: JavaScript；页 None–None
  - 原文：JS can be executed in runtime environments outside the browser.
  - Block IDs：fcd53cb4-9f4b-5974-b2f4-1a950acea7f8；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_045 — zh_to_en

不打开浏览器窗口也能运行网页应用格式的独立程序，资料指的是哪个系统工具？

参考答案：Mshta.exe executes HTA files; HTAs run outside the browser.
语言：zh → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：mshta-files|mshta-outside
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-mshta-files` — attack_t1218_005.md；章节 T1218.005: Mshta；页 None–None
  - 原文：Mshta.exe is a utility that executes Microsoft HTML Applications (HTA) files.
  - Block IDs：916b2462-09e9-58bd-b32a-693403d57ece；同义位置 0 个
- `security-v1-mshta-outside` — attack_t1218_005.md；章节 T1218.005: Mshta；页 None–None
  - 原文：HTAs are standalone applications that execute using the same models and technologies of Internet Explorer, but outside of the browser.
  - Block IDs：916b2462-09e9-58bd-b32a-693403d57ece；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_046 — zh_to_en

攻击者借用合法账号连接远程管理机制后，会以哪个登录身份执行后续操作？

参考答案：WinRM interactions can perform actions as the logged-on user.
语言：zh → en；主题：remote_execution；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：winrm-user
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-winrm-user` — attack_t1021_006.md；章节 T1021.006: Windows Remote Management；页 None–None
  - 原文：The adversary may then perform actions as the logged-on user.
  - Block IDs：5715ec94-c4dd-5041-8ff5-ef73da333d7e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_047 — zh_to_en

远程管理机制除了启动程序，还允许对目标系统的哪两类配置进行修改？

参考答案：WinRM can modify the Registry and services.
语言：zh → en；主题：remote_execution；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：winrm-service
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-winrm-service` — attack_t1021_006.md；章节 T1021.006: Windows Remote Management；页 None–None
  - 原文：WinRM is the name of both a Windows service and a protocol that allows a user to interact with a remote system (e.g., run an executable, modify the Registry, modify services).
  - Block IDs：155a22f7-ddaa-5ca0-9cfd-da4e5d13dd8e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_048 — zh_to_en

不是向用户登录目录放文件，而是借助系统服务管理接口来启动载荷，这对应什么执行机制？

参考答案：Service Execution abuses the Windows service control manager.
语言：zh → en；主题：execution；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：service-manager
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-service-manager` — attack_t1569_002.md；章节 T1569.002: Service Execution；页 None–None
  - 原文：Adversaries may abuse the Windows service control manager to execute malicious commands or payloads.
  - Block IDs：b7322e98-245d-599b-84cf-6a98ab684753；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_049 — zh_to_en

数据库结果不直接出现在页面中时，测试者可以通过什么观察方式重建信息？

参考答案：Inferential/blind injection sends requests and observes database behaviour.
语言：zh → en；主题：sql_injection；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：blind
干扰来源：未指定专用干扰源；仍检索完整语料

- `owasp_wstg_v4_2_sql_injection-b17-1` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > Summary；页 None–None
  - 原文：Inferential or Blind: there is no actual transfer of data, but the tester is able to reconstruct the information by sending particular requests and observing the resulting behavior of the DB Server.
  - Block IDs：43da13f1-0522-5462-9973-325458b7c9e8；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_050 — zh_to_en

查询结果不沿着提交输入的页面返回，而是另走一条通信通道，这属于哪种取数方式？

参考答案：Out-of-band SQL injection retrieves data through a different channel.
语言：zh → en；主题：sql_injection；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：oob
干扰来源：未指定专用干扰源；仍检索完整语料

- `owasp_wstg_v4_2_sql_injection-b16-2` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > Summary；页 None–None
  - 原文：Out-of-band: data is retrieved using a different channel
  - Block IDs：f2a22a75-f5e5-51f3-a548-4d7639e958b8；同义位置 1 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_051 — zh_to_en

梳理可能进入数据库查询的入口时，只查看可见输入框够不够，还应考虑哪些隐藏或附带的请求内容？

参考答案：Include hidden POST fields, HTTP headers and cookies, and test input fields separately.
语言：zh → en；主题：sql_injection；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：input-surface
干扰来源：未指定专用干扰源；仍检索完整语料

- `owasp_wstg_v4_2_sql_injection-b34-1` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > How to Test > Detection Techniques；页 None–None
  - 原文：The tester has to make a list of all input fields whose values could be used in crafting a SQL query, including the hidden fields of POST requests and then test them separately, trying to interfere with the query and to generate an error. Consider also HTTP headers and Cookies.
  - Block IDs：2a3b25de-590d-55a4-a251-2cfef4274def；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_052 — zh_to_en

恢复工作尚未结束时，已经发现的改进经验应当什么时候分享，而不是等待什么节点？

参考答案：Share lessons as soon as identified; do not delay until recovery concludes.
语言：zh → en；主题：incident_response；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：lessons
干扰来源：未指定专用干扰源；仍检索完整语料

- `nist_sp80061r3_pp10-12-b38-1` — nist_sp80061r3_pp10-12.pdf；章节 2. Incident Response as Part of Cybersecurity Risk Management > 2.1. Incident Response Life Cycle Model；页 3–3
  - 原文：The lessons learned during incident response should often be shared as soon as they are identified, not delayed until after recovery concludes.
  - Block IDs：f6162960-05d9-52ae-9d47-a71be9bf79ae；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_053 — zh_to_en

为什么一本固定出版物不再适合维护所有事件处置的操作细节？

参考答案：Response details change often and vary across technologies, environments and organizations.
语言：zh → en；主题：incident_response；难度：medium
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：static-publication
干扰来源：未指定专用干扰源；仍检索完整语料

- `nist_sp80061r3_pp10-12-b14-1` — nist_sp80061r3_pp10-12.pdf；章节 1. Introduction > 1.1. Purpose and Scope；页 2–2
  - 原文：Because the details of how to perform incident response activities change so often and vary so much across technologies, environments, and organizations, it is no longer feasible to capture and maintain that information in a single static publication.
  - Block IDs：4a0e88f0-2723-5bcc-83f6-e62e853990cc；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_054 — zh_to_en

恶意软件事件处理完后，已受影响的认证材料和用于恢复的数据副本分别该如何处理？

参考答案：Reset compromised credentials and restore from clean backups.
语言：zh → en；主题：incident_response；难度：hard
状态：pending；审核人：未填写
设计说明：Natural Chinese security-analysis query over English evidence; no technique ID in query.
查询族：backup|reset
干扰来源：未指定专用干扰源；仍检索完整语料

- `malware-b17-1` — malware.md；章节 Malware > Response；页 None–None
  - 原文：Reset compromised credentials
  - Block IDs：cddc7cd0-ca46-5b71-9ce2-04c512eba076；同义位置 0 个
- `malware-b18-2` — malware.md；章节 Malware > Response；页 None–None
  - 原文：Restore systems from clean backups
  - Block IDs：192826d3-d01b-531a-b2f0-c19e1f69f940；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_055 — mixed_terms

cmd.exe 的 .bat/.cmd 文件能否承载顺序任务、条件分支和循环？

参考答案：Yes; batch files support sequential commands, conditionals and loops.
语言：mixed → en；主题：execution；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：batch
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-batch` — attack_t1059_003.md；章节 T1059.003: Windows Command Shell；页 None–None
  - 原文：Batch files (ex: .bat or .cmd) also provide the shell with a list of sequential commands to run, as well as normal scripting operations such as conditionals and loops.
  - Block IDs：04113221-c298-563b-8678-db6e7818695e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_056 — mixed_terms

VBA macro 为什么能让 Office 文档自动执行宿主机上的任务？

参考答案：VBA is event-driven and enables task-automation macros in documents.
语言：mixed → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：vba-event|vba-macros
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-vba-event` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA is an event-driven programming language built into Microsoft Office, as well as several third-party applications.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- `security-v1-vba-macros` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA enables documents to contain macros used to automate the execution of tasks and other functionality on the host.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_057 — mixed_terms

JScript 在 Windows 里由哪个脚本引擎解释，而不只是被当成网页代码？

参考答案：The Windows Script engine.
语言：mixed → en；主题：execution；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：js-engine
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-js-engine` — attack_t1059_007.md；章节 T1059.007: JavaScript；页 None–None
  - 原文：JScript is interpreted via the Windows Script engine
  - Block IDs：00d584fe-35bb-545c-8774-d5b3bad70fae；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_058 — mixed_terms

mshta.exe 对 .hta 文件的作用是什么？这些应用一定要在浏览器内部执行吗？

参考答案：It executes HTA files, which run outside the browser.
语言：mixed → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：mshta-files|mshta-outside
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-mshta-files` — attack_t1218_005.md；章节 T1218.005: Mshta；页 None–None
  - 原文：Mshta.exe is a utility that executes Microsoft HTML Applications (HTA) files.
  - Block IDs：916b2462-09e9-58bd-b32a-693403d57ece；同义位置 0 个
- `security-v1-mshta-outside` — attack_t1218_005.md；章节 T1218.005: Mshta；页 None–None
  - 原文：HTAs are standalone applications that execute using the same models and technologies of Internet Explorer, but outside of the browser.
  - Block IDs：916b2462-09e9-58bd-b32a-693403d57ece；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_059 — mixed_terms

WinRM 不只是 PowerShell 命令名，它在系统里同时代表哪两种东西？

参考答案：Both a Windows service and a remote interaction protocol.
语言：mixed → en；主题：remote_execution；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：winrm-service
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-winrm-service` — attack_t1021_006.md；章节 T1021.006: Windows Remote Management；页 None–None
  - 原文：WinRM is the name of both a Windows service and a protocol that allows a user to interact with a remote system (e.g., run an executable, modify the Registry, modify services).
  - Block IDs：155a22f7-ddaa-5ca0-9cfd-da4e5d13dd8e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_060 — mixed_terms

PsExec 借助 SCM 创建临时 Windows service 后，利用什么机制运行命令或载荷？

参考答案：By creating a temporary Windows service through the service control manager API.
语言：mixed → en；主题：execution；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：service-psexec
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-service-psexec` — attack_t1569_002.md；章节 T1569.002: Service Execution；页 None–None
  - 原文：can also be used to execute commands or payloads via a temporary Windows service created through the service control manager API.
  - Block IDs：04a70cc9-bc44-523f-8f51-b9e5579402d4；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_061 — mixed_terms

Password Spraying 中为什么每个 account 的尝试次数会刻意压低？

参考答案：To avoid account lockouts from many passwords against one account.
语言：mixed → en；主题：authentication；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：spray-lockout
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-spray-lockout` — attack_t1110_003.md；章节 T1110.003: Password Spraying；页 None–None
  - 原文：Logins are attempted with that password against many different accounts on a network to avoid account lockouts that would normally occur when brute forcing a single account with many passwords.
  - Block IDs：56673f90-6e84-5f53-a039-486e18269926；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_062 — mixed_terms

Credential Stuffing 使用 breach dump 后，认证失败和账号锁定方面有什么风险？

参考答案：It can cause numerous authentication failures and account lockouts depending on login failure policies.
语言：mixed → en；主题：authentication；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：stuffing-lockout
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-stuffing-lockout` — attack_t1110_004.md；章节 T1110.004: Credential Stuffing；页 None–None
  - 原文：Credential stuffing is a risky option because it could cause numerous authentication failures and account lockouts, depending on the organization's login failure policies.
  - Block IDs：a25ba1c6-b093-512d-b39c-9cb94610489e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_063 — mixed_terms

Pass-the-Hash 能否在不知道 cleartext password 的情况下冒用身份认证？

参考答案：Yes; it authenticates using a password hash without access to the cleartext password.
语言：mixed → en；主题：credential_access；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：pth-auth
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-pth-auth` — attack_t1550_002.md；章节 T1550.002: Pass the Hash；页 None–None
  - 原文：Pass the hash (PtH) is a method of authenticating as a user without having access to the user's cleartext password.
  - Block IDs：a7b92d0e-65b1-5b80-9e49-dd5014661713；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_064 — mixed_terms

LSASS 的 credential material 在什么事件后生成并保留在进程内存？

参考答案：After a user logs on.
语言：mixed → en；主题：credential_access；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：lsass-memory
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-lsass-memory` — attack_t1003_001.md；章节 T1003.001: LSASS Memory；页 None–None
  - 原文：After a user logs on, the system generates and stores a variety of credential materials in LSASS process memory.
  - Block IDs：fd740129-64cf-5f89-8c24-62cf6b963a07；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_065 — mixed_terms

Registry Run key 引用的程序在 logon 时运行，继承的是哪个 account context？

参考答案：The user context and its associated permissions.
语言：mixed → en；主题：persistence；难度：hard
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：run-context|run-logon
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-run-logon` — attack_t1547_001.md；章节 T1547.001: Registry Run Keys / Startup Folder；页 None–None
  - 原文：Adding an entry to the "run keys" in the Registry or startup folder will cause the program referenced to be executed when a user logs in.
  - Block IDs：8463fc42-6ce3-59a2-9c2b-c2263af4c057；同义位置 0 个
- `security-v1-run-context` — attack_t1547_001.md；章节 T1547.001: Registry Run Keys / Startup Folder；页 None–None
  - 原文：These programs will be executed under the context of the user and will have the account's associated permissions level.
  - Block IDs：8463fc42-6ce3-59a2-9c2b-c2263af4c057；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_066 — mixed_terms

Base64 或 URL encoding 在 Command Obfuscation 中起什么作用？

参考答案：They are built-in forms of obfuscation that make command strings and patterns harder to signature and analyze.
语言：mixed → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：obfuscation-encoding|obfuscation-purpose
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-obfuscation-purpose` — attack_t1027_010.md；章节 T1027.010: Command Obfuscation；页 None–None
  - 原文：Command-line obfuscation is a method of making strings and patterns within commands and scripts more difficult to signature and analyze.
  - Block IDs：17ccfa8c-82d7-52ff-bb3b-70f5497deb59；同义位置 0 个
- `security-v1-obfuscation-encoding` — attack_t1027_010.md；章节 T1027.010: Command Obfuscation；页 None–None
  - 原文：Many languages support built-in obfuscation in the form of base64 or URL encoding.
  - Block IDs：0ba1a784-0fc3-5421-baf1-fe6b55bb6ebc；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_067 — mixed_terms

LSASS memory dump 可以只在目标主机当场分析吗，还是能够离线转移分析？

参考答案：LSASS memory can be dumped from the target and analyzed on a local system.
语言：mixed → en；主题：credential_access；难度：medium
状态：pending；审核人：未填写
设计说明：Chinese analysis wording with retained operational English terms; require the cited fact, not keyword neighbours.
查询族：lsass-dump
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-lsass-dump` — attack_t1003_001.md；章节 T1003.001: LSASS Memory；页 None–None
  - 原文：As well as in-memory techniques, the LSASS process memory can be dumped from the target host and analyzed on a local system.
  - Block IDs：d35813f4-15d2-5805-a164-d0ac69121661；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_068 — paraphrase

有没有办法让一个程序在用户开始新的桌面会话时自己再次运行，而不需要用户亲手启动它？

参考答案：A Registry run key or startup-folder entry launches the referenced program when the user logs in.
语言：zh → en；主题：persistence；难度：hard
状态：pending；审核人：未填写
设计说明：Indirect description omits the source heading; preserve exact fact support. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：run-logon
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-run-logon` — attack_t1547_001.md；章节 T1547.001: Registry Run Keys / Startup Folder；页 None–None
  - 原文：Adding an entry to the "run keys" in the Registry or startup folder will cause the program referenced to be executed when a user logs in.
  - Block IDs：8463fc42-6ce3-59a2-9c2b-c2263af4c057；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_069 — paraphrase

How can a stolen secret stand in for the characters its owner originally typed when a service authenticates that owner?

参考答案：Pass the Hash authenticates with a stolen password hash without the cleartext password.
语言：en → en；主题：credential_access；难度：hard
状态：pending；审核人：未填写
设计说明：Indirect description omits the source heading; preserve exact fact support.
查询族：pth-auth
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-pth-auth` — attack_t1550_002.md；章节 T1550.002: Pass the Hash；页 None–None
  - 原文：Pass the hash (PtH) is a method of authenticating as a user without having access to the user's cleartext password.
  - Block IDs：a7b92d0e-65b1-5b80-9e49-dd5014661713；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_070 — paraphrase

为什么攻击者会把一份很短的猜测清单分散用于许多身份，而不把所有尝试押在同一个身份上？

参考答案：To avoid account lockouts associated with many password guesses against a single account.
语言：zh → en；主题：authentication；难度：hard
状态：pending；审核人：未填写
设计说明：Indirect description omits the source heading; preserve exact fact support. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：spray-lockout
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-spray-lockout` — attack_t1110_003.md；章节 T1110.003: Password Spraying；页 None–None
  - 原文：Logins are attempted with that password against many different accounts on a network to avoid account lockouts that would normally occur when brute forcing a single account with many passwords.
  - Block IDs：56673f90-6e84-5f53-a039-486e18269926；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_071 — paraphrase

Why can an unrelated website leak create a second opportunity to enter an organization through employee logins?

参考答案：Users may reuse passwords across personal and business accounts; credential stuffing exploits this overlap.
语言：en → en；主题：authentication；难度：hard
状态：pending；审核人：未填写
设计说明：Indirect description omits the source heading; preserve exact fact support.
查询族：stuffing-cause|stuffing-reuse
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-stuffing-reuse` — attack_t1110_004.md；章节 T1110.004: Credential Stuffing；页 None–None
  - 原文：Adversaries may use credentials obtained from breach dumps of unrelated accounts to gain access to target accounts through credential overlap.
  - Block IDs：998cc467-f643-58aa-938a-2e1e23e1c412；同义位置 0 个
- `security-v1-stuffing-cause` — attack_t1110_004.md；章节 T1110.004: Credential Stuffing；页 None–None
  - 原文：taking advantage of the tendency for users to use the same passwords across personal and business accounts.
  - Block IDs：998cc467-f643-58aa-938a-2e1e23e1c412；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_072 — paraphrase

办公文件原本只是内容载体，哪种内置能力能让它在特定事件发生时自动执行主机任务？

参考答案：VBA macros in Office documents can automate host tasks.
语言：zh → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Indirect description omits the source heading; preserve exact fact support. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：vba-event|vba-macros
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-vba-event` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA is an event-driven programming language built into Microsoft Office, as well as several third-party applications.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- `security-v1-vba-macros` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA enables documents to contain macros used to automate the execution of tasks and other functionality on the host.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_073 — paraphrase

Why is a login using an existing identity not enough to conclude that access controls kept an intruder out?

参考答案：Compromised credentials may be used to bypass access controls.
语言：en → en；主题：account_abuse；难度：hard
状态：pending；审核人：未填写
设计说明：Indirect description omits the source heading; preserve exact fact support.
查询族：controls
干扰来源：未指定专用干扰源；仍检索完整语料

- `mitre_attack_v17_1-b34-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts；页 None–None
  - 原文：Compromised credentials may be used to bypass access controls
  - Block IDs：9df49cee-b541-5e50-a1db-22159ec3bf17；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_074 — paraphrase

不去猜用户的口令，而是寻找已经登录的会话留下的秘密，应查看哪里，又需要哪类身份才能提取？

参考答案：Credential materials are stored in LSASS process memory and can be harvested by an administrative user or SYSTEM.
语言：zh → en；主题：credential_access；难度：hard
状态：pending；审核人：未填写
设计说明：Indirect description omits the source heading; preserve exact fact support. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：lsass-memory|lsass-rights
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-lsass-memory` — attack_t1003_001.md；章节 T1003.001: LSASS Memory；页 None–None
  - 原文：After a user logs on, the system generates and stores a variety of credential materials in LSASS process memory.
  - Block IDs：fd740129-64cf-5f89-8c24-62cf6b963a07；同义位置 0 个
- `security-v1-lsass-rights` — attack_t1003_001.md；章节 T1003.001: LSASS Memory；页 None–None
  - 原文：These credential materials can be harvested by an administrative user or SYSTEM
  - Block IDs：fd740129-64cf-5f89-8c24-62cf6b963a07；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_075 — paraphrase

How can a saved command list repeat desktop tasks and make choices without an operator typing every instruction again?

参考答案：Windows command-shell batch files provide sequential commands, conditionals and loops.
语言：en → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Indirect description omits the source heading; preserve exact fact support.
查询族：batch
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-batch` — attack_t1059_003.md；章节 T1059.003: Windows Command Shell；页 None–None
  - 原文：Batch files (ex: .bat or .cmd) also provide the shell with a list of sequential commands to run, as well as normal scripting operations such as conditionals and loops.
  - Block IDs：04113221-c298-563b-8678-db6e7818695e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_076 — technique_confusion

What account attack tries the same few common passwords across identities to avoid per-account lockout?

参考答案：Password spraying.
语言：en → en；主题：authentication；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：spray-lockout|spray-pattern
干扰来源：attack_t1110_004.md

- `security-v1-spray-pattern` — attack_t1110_003.md；章节 T1110.003: Password Spraying；页 None–None
  - 原文：Adversaries may use a single or small list of commonly used passwords against many different accounts to attempt to acquire valid account credentials.
  - Block IDs：56673f90-6e84-5f53-a039-486e18269926；同义位置 0 个
- `security-v1-spray-lockout` — attack_t1110_003.md；章节 T1110.003: Password Spraying；页 None–None
  - 原文：Logins are attempted with that password against many different accounts on a network to avoid account lockouts that would normally occur when brute forcing a single account with many passwords.
  - Block IDs：56673f90-6e84-5f53-a039-486e18269926；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_077 — technique_confusion

攻击者已经拿到外站泄露的成对账号密码，再利用用户复用习惯登录目标；这与轮试常见口令的模式如何区分？

参考答案：Credential stuffing uses breach-dump credentials and password overlap.
语言：zh → en；主题：authentication；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword.
查询族：stuffing-cause|stuffing-reuse
干扰来源：attack_t1110_003.md

- `security-v1-stuffing-reuse` — attack_t1110_004.md；章节 T1110.004: Credential Stuffing；页 None–None
  - 原文：Adversaries may use credentials obtained from breach dumps of unrelated accounts to gain access to target accounts through credential overlap.
  - Block IDs：998cc467-f643-58aa-938a-2e1e23e1c412；同义位置 0 个
- `security-v1-stuffing-cause` — attack_t1110_004.md；章节 T1110.004: Credential Stuffing；页 None–None
  - 原文：taking advantage of the tendency for users to use the same passwords across personal and business accounts.
  - Block IDs：998cc467-f643-58aa-938a-2e1e23e1c412；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_078 — technique_confusion

Which technique uses a stolen hash to authenticate directly rather than cracking it back into a password?

参考答案：Pass the Hash authenticates without the cleartext password.
语言：en → en；主题：credential_access；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：pth-auth
干扰来源：mitre_attack_v17_1.md, attack_t1003_001.md

- `security-v1-pth-auth` — attack_t1550_002.md；章节 T1550.002: Pass the Hash；页 None–None
  - 原文：Pass the hash (PtH) is a method of authenticating as a user without having access to the user's cleartext password.
  - Block IDs：a7b92d0e-65b1-5b80-9e49-dd5014661713；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_079 — technique_confusion

分析目标是获取已登录会话留下的内存凭据，而不是使用现成摘要去认证；应该聚焦哪个安全进程？

参考答案：LSASS process memory.
语言：zh → en；主题：credential_access；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword.
查询族：lsass-memory
干扰来源：attack_t1550_002.md

- `security-v1-lsass-memory` — attack_t1003_001.md；章节 T1003.001: LSASS Memory；页 None–None
  - 原文：After a user logs on, the system generates and stores a variety of credential materials in LSASS process memory.
  - Block IDs：fd740129-64cf-5f89-8c24-62cf6b963a07；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_080 — technique_confusion

Which language mechanism best fits event-driven macros embedded in Office documents rather than webpage scripts?

参考答案：Visual Basic for Applications (VBA) macros.
语言：en → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：vba-event|vba-macros
干扰来源：attack_t1059_007.md, attack_t1218_005.md

- `security-v1-vba-event` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA is an event-driven programming language built into Microsoft Office, as well as several third-party applications.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- `security-v1-vba-macros` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA enables documents to contain macros used to automate the execution of tasks and other functionality on the host.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_081 — technique_confusion

线索明确是由系统脚本引擎解释的微软脚本实现，而非办公文档宏；应找哪个实现？

参考答案：JScript.
语言：zh → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword.
查询族：js-engine
干扰来源：attack_t1059_005.md

- `security-v1-js-engine` — attack_t1059_007.md；章节 T1059.007: JavaScript；页 None–None
  - 原文：JScript is interpreted via the Windows Script engine
  - Block IDs：00d584fe-35bb-545c-8774-d5b3bad70fae；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_082 — technique_confusion

Which mechanism uses batch files with sequential commands and loops rather than PowerShell cmdlets?

参考答案：Windows command-shell batch files (.bat or .cmd).
语言：en → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：batch
干扰来源：mitre_attack_v17_1.md

- `security-v1-batch` — attack_t1059_003.md；章节 T1059.003: Windows Command Shell；页 None–None
  - 原文：Batch files (ex: .bat or .cmd) also provide the shell with a list of sequential commands to run, as well as normal scripting operations such as conditionals and loops.
  - Block IDs：04113221-c298-563b-8678-db6e7818695e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_083 — technique_confusion

需要远程修改注册表和服务，线索指向一种同名的系统服务与协议，而非仅仅本地命令解释器；它是什么？

参考答案：Windows Remote Management (WinRM).
语言：zh → en；主题：remote_execution；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword.
查询族：winrm-service
干扰来源：attack_t1059_003.md, attack_t1569_002.md

- `security-v1-winrm-service` — attack_t1021_006.md；章节 T1021.006: Windows Remote Management；页 None–None
  - 原文：WinRM is the name of both a Windows service and a protocol that allows a user to interact with a remote system (e.g., run an executable, modify the Registry, modify services).
  - Block IDs：155a22f7-ddaa-5ca0-9cfd-da4e5d13dd8e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_084 — technique_confusion

What persistence location executes a referenced program at user logon with that user permissions rather than via a temporary remote service?

参考答案：Registry run keys or startup folders.
语言：en → en；主题：persistence；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：run-context|run-logon
干扰来源：attack_t1569_002.md

- `security-v1-run-logon` — attack_t1547_001.md；章节 T1547.001: Registry Run Keys / Startup Folder；页 None–None
  - 原文：Adding an entry to the "run keys" in the Registry or startup folder will cause the program referenced to be executed when a user logs in.
  - Block IDs：8463fc42-6ce3-59a2-9c2b-c2263af4c057；同义位置 0 个
- `security-v1-run-context` — attack_t1547_001.md；章节 T1547.001: Registry Run Keys / Startup Folder；页 None–None
  - 原文：These programs will be executed under the context of the user and will have the account's associated permissions level.
  - Block IDs：8463fc42-6ce3-59a2-9c2b-c2263af4c057；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_085 — technique_confusion

载荷通过服务管理器的临时服务运行，不是等用户下次登录；资料中对应什么执行方式？

参考答案：Service Execution; PsExec can create a temporary service through the SCM API.
语言：zh → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword.
查询族：service-psexec
干扰来源：attack_t1547_001.md

- `security-v1-service-psexec` — attack_t1569_002.md；章节 T1569.002: Service Execution；页 None–None
  - 原文：can also be used to execute commands or payloads via a temporary Windows service created through the service control manager API.
  - Block IDs：04a70cc9-bc44-523f-8f51-b9e5579402d4；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_086 — technique_confusion

Which system scripting environment can download and execute programs in memory without touching disk, unlike batch-file or logon-entry mechanisms?

参考答案：PowerShell.
语言：en → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：ps-memory
干扰来源：attack_t1059_003.md, attack_t1547_001.md

- `mitre_attack_v17_1-b7-1` — mitre_attack_v17_1.md；章节 MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell；页 None–None
  - 原文：PowerShell may also be used to download and run executables from the Internet, which can be executed from disk or in memory without touching disk.
  - Block IDs：33fd520c-129b-5f4b-8df8-a97aacf70b18；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_087 — technique_confusion

现象是把原来可识别的命令改写成难以签名的编码或字符串形式，而不是换一个脚本宿主；这描述哪种目的？

参考答案：Command obfuscation impedes signature matching and analysis.
语言：zh → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword.
查询族：obfuscation-purpose
干扰来源：attack_t1059_003.md, mitre_attack_v17_1.md

- `security-v1-obfuscation-purpose` — attack_t1027_010.md；章节 T1027.010: Command Obfuscation；页 None–None
  - 原文：Command-line obfuscation is a method of making strings and patterns within commands and scripts more difficult to signature and analyze.
  - Block IDs：17ccfa8c-82d7-52ff-bb3b-70f5497deb59；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_088 — technique_confusion

Which retrieval method reconstructs information from database behaviour without receiving it through another channel?

参考答案：Inferential/blind SQL injection.
语言：en → en；主题：sql_injection；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：blind
干扰来源：sql_injection.md

- `owasp_wstg_v4_2_sql_injection-b17-1` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > Summary；页 None–None
  - 原文：Inferential or Blind: there is no actual transfer of data, but the tester is able to reconstruct the information by sending particular requests and observing the resulting behavior of the DB Server.
  - Block IDs：43da13f1-0522-5462-9973-325458b7c9e8；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_089 — technique_confusion

目标将查询结果交给另一条通信链路，而不是直接显示在提交输入的原页面；应归为哪一类？

参考答案：Out-of-band.
语言：zh → en；主题：sql_injection；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword.
查询族：oob
干扰来源：sql_injection.md

- `owasp_wstg_v4_2_sql_injection-b16-2` — owasp_wstg_v4_2_sql_injection.md；章节 Testing for SQL Injection > Summary；页 None–None
  - 原文：Out-of-band: data is retrieved using a different channel
  - Block IDs：f2a22a75-f5e5-51f3-a548-4d7639e958b8；同义位置 1 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_090 — technique_confusion

Which trusted Windows utility executes standalone HTA files rather than Office document macros?

参考答案：Mshta.exe.
语言：en → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Discriminate the described behaviour from a declared similar but wrong source; do not credit a shared keyword. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：mshta-files|mshta-outside
干扰来源：attack_t1059_005.md, attack_t1059_007.md

- `security-v1-mshta-files` — attack_t1218_005.md；章节 T1218.005: Mshta；页 None–None
  - 原文：Mshta.exe is a utility that executes Microsoft HTML Applications (HTA) files.
  - Block IDs：916b2462-09e9-58bd-b32a-693403d57ece；同义位置 0 个
- `security-v1-mshta-outside` — attack_t1218_005.md；章节 T1218.005: Mshta；页 None–None
  - 原文：HTAs are standalone applications that execute using the same models and technologies of Internet Explorer, but outside of the browser.
  - Block IDs：916b2462-09e9-58bd-b32a-693403d57ece；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_091 — unanswerable

我们租户当前到底连续失败几次才会锁定账号，锁定持续多少分钟？

参考答案：Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
语言：zh → none；主题：authentication；难度：hard
状态：pending；审核人：未填写
设计说明：Corpus contains related guidance but no tenant/host-specific observations; empty positive evidence is intentional.
查询族：gap-rag_091
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_092 — unanswerable

这次内存采集实际提取到了哪些域用户的密码摘要？

参考答案：Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
语言：zh → none；主题：credential_access；难度：hard
状态：pending；审核人：未填写
设计说明：Corpus contains related guidance but no tenant/host-specific observations; empty positive evidence is intentional.
查询族：gap-rag_092
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_093 — unanswerable

终端 SEC-WS-17 上的登录自启动条目是谁在什么时间写入的？

参考答案：Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
语言：zh → none；主题：persistence；难度：hard
状态：pending；审核人：未填写
设计说明：Corpus contains related guidance but no tenant/host-specific observations; empty positive evidence is intentional.
查询族：gap-rag_093
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_094 — unanswerable

昨晚触发编码脚本告警的外部来源地址具体是多少？

参考答案：Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
语言：zh → none；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Corpus contains related guidance but no tenant/host-specific observations; empty positive evidence is intentional.
查询族：gap-rag_094
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_095 — unanswerable

本次主机隔离是否已经由值班人员实际执行成功？

参考答案：Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
语言：zh → none；主题：incident_response；难度：hard
状态：pending；审核人：未填写
设计说明：Corpus contains related guidance but no tenant/host-specific observations; empty positive evidence is intentional.
查询族：gap-rag_095
干扰来源：未指定专用干扰源；仍检索完整语料

- 无正向证据；不得将邻近指导文档标作本事件事实。
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_096 — multi_document

Separate two stages: which process stores credential materials after logon, and how can captured hashes then authenticate without the cleartext password?

参考答案：LSASS process memory stores credential materials after logon; Pass the Hash authenticates as a user without the cleartext password.
语言：en → en；主题：credential_access；难度：hard
状态：pending；审核人：未填写
设计说明：Every listed fact is necessary; no single source can fully answer both parts. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：lsass-memory|pth-auth
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-lsass-memory` — attack_t1003_001.md；章节 T1003.001: LSASS Memory；页 None–None
  - 原文：After a user logs on, the system generates and stores a variety of credential materials in LSASS process memory.
  - Block IDs：fd740129-64cf-5f89-8c24-62cf6b963a07；同义位置 0 个
- `security-v1-pth-auth` — attack_t1550_002.md；章节 T1550.002: Pass the Hash；页 None–None
  - 原文：Pass the hash (PtH) is a method of authenticating as a user without having access to the user's cleartext password.
  - Block IDs：a7b92d0e-65b1-5b80-9e49-dd5014661713；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_097 — multi_document

请分别说明用户登录自启动程序的触发时机，以及远程管理机制可修改的两类系统配置，不要把两种机制混为一谈。

参考答案：Run-key/startup programs execute at user logon; WinRM can modify the Registry and services.
语言：zh → en；主题：remote_execution；难度：hard
状态：pending；审核人：未填写
设计说明：Every listed fact is necessary; no single source can fully answer both parts.
查询族：run-logon|winrm-service
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-run-logon` — attack_t1547_001.md；章节 T1547.001: Registry Run Keys / Startup Folder；页 None–None
  - 原文：Adding an entry to the "run keys" in the Registry or startup folder will cause the program referenced to be executed when a user logs in.
  - Block IDs：8463fc42-6ce3-59a2-9c2b-c2263af4c057；同义位置 0 个
- `security-v1-winrm-service` — attack_t1021_006.md；章节 T1021.006: Windows Remote Management；页 None–None
  - 原文：WinRM is the name of both a Windows service and a protocol that allows a user to interact with a remote system (e.g., run an executable, modify the Registry, modify services).
  - Block IDs：155a22f7-ddaa-5ca0-9cfd-da4e5d13dd8e；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_098 — multi_document

针对恶意软件事件，网络、认证材料和恢复副本应分别如何处理；已经发现的经验教训是否要等恢复结束才分享？

参考答案：Isolate affected systems from the network, reset compromised credentials and restore clean backups; share identified lessons promptly rather than wait for recovery completion.
语言：zh → en；主题：incident_response；难度：hard
状态：pending；审核人：未填写
设计说明：Every listed fact is necessary; no single source can fully answer both parts.
查询族：backup|isolate|lessons|reset
干扰来源：未指定专用干扰源；仍检索完整语料

- `malware-b14-1` — malware.md；章节 Malware > Response；页 None–None
  - 原文：Isolate affected systems from the network
  - Block IDs：673d2578-1560-51e1-a55a-1323de1d3798；同义位置 0 个
- `malware-b17-1` — malware.md；章节 Malware > Response；页 None–None
  - 原文：Reset compromised credentials
  - Block IDs：cddc7cd0-ca46-5b71-9ce2-04c512eba076；同义位置 0 个
- `malware-b18-2` — malware.md；章节 Malware > Response；页 None–None
  - 原文：Restore systems from clean backups
  - Block IDs：192826d3-d01b-531a-b2f0-c19e1f69f940；同义位置 0 个
- `nist_sp80061r3_pp10-12-b38-1` — nist_sp80061r3_pp10-12.pdf；章节 2. Incident Response as Part of Cybersecurity Risk Management > 2.1. Incident Response Life Cycle Model；页 3–3
  - 原文：The lessons learned during incident response should often be shared as soon as they are identified, not delayed until after recovery concludes.
  - Block IDs：f6162960-05d9-52ae-9d47-a71be9bf79ae；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_099 — multi_document

Distinguish event-driven Office document macros from the Microsoft scripting implementation interpreted by the Windows Script engine.

参考答案：VBA is event-driven and provides Office macros; JScript is interpreted by the Windows Script engine.
语言：en → en；主题：execution；难度：hard
状态：pending；审核人：未填写
设计说明：Every listed fact is necessary; no single source can fully answer both parts. Balanced-language design revision: fixed ID rotation, not selected by retrieval success; answer/evidence unchanged.
查询族：js-engine|vba-event|vba-macros
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-vba-event` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA is an event-driven programming language built into Microsoft Office, as well as several third-party applications.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- `security-v1-vba-macros` — attack_t1059_005.md；章节 T1059.005: Visual Basic；页 None–None
  - 原文：VBA enables documents to contain macros used to automate the execution of tasks and other functionality on the host.
  - Block IDs：5c51f771-6fdc-582c-a394-04c3aafe35ff；同义位置 0 个
- `security-v1-js-engine` — attack_t1059_007.md；章节 T1059.007: JavaScript；页 None–None
  - 原文：JScript is interpreted via the Windows Script engine
  - Block IDs：00d584fe-35bb-545c-8774-d5b3bad70fae；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。

## rag_100 — multi_document

先说明少量常见口令遍历许多身份的行为模式，再列出本地暴力破解清单的三项建议；不要声称每项措施与某个指标一一对应。

参考答案：Password spraying uses a small password set against many accounts; the local guide recommends blocking suspicious IPs, enabling MFA and investigating affected accounts.
语言：zh → en；主题：authentication；难度：hard
状态：pending；审核人：未填写
设计说明：Every listed fact is necessary; no single source can fully answer both parts.
查询族：block-ip|investigate|mfa|spray-pattern
干扰来源：未指定专用干扰源；仍检索完整语料

- `security-v1-spray-pattern` — attack_t1110_003.md；章节 T1110.003: Password Spraying；页 None–None
  - 原文：Adversaries may use a single or small list of commonly used passwords against many different accounts to attempt to acquire valid account credentials.
  - Block IDs：56673f90-6e84-5f53-a039-486e18269926；同义位置 0 个
- `brute_force-b10-1` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Block suspicious IP
  - Block IDs：c74f8193-1c4e-505f-8635-a2ee3765eb35；同义位置 0 个
- `brute_force-b11-2` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Enable MFA
  - Block IDs：e4c5acd1-6a01-5eb2-b76f-921c176f8483；同义位置 0 个
- `brute_force-b12-3` — brute_force.md；章节 Brute Force Attack > Response；页 None–None
  - 原文：Investigate affected accounts
  - Block IDs：fdc90658-40c0-5122-b255-1b934a93812b；同义位置 0 个
- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。


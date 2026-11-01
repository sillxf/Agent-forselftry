# Candidate annotation review sheet

**All items are pending human review.** This sheet is a reading aid; edit `questions.jsonl` as the source of truth.
Check alternate valid evidence and unanswerable rationales, then record the real reviewer and bump dataset version.

## rag_001 — exact_identifier

T1059.001 refers to which Windows scripting environment?

Expected answer: PowerShell.
Rationale: The selected ATT&CK technique heading gives the identifier and name.
Answerable: True; review: pending

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b1-1`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell
  - Source block IDs: `c2440acc-92b4-55a1-8358-fc947f7295d9`
  - Quote: T1059.001: PowerShell

## rag_002 — exact_identifier

What technique is assigned the ATT&CK identifier T1110?

Expected answer: Brute Force.
Rationale: The pinned ATT&CK heading provides the identifier mapping.
Answerable: True; review: pending

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b20-1`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1110: Brute Force
  - Source block IDs: `a48dc3aa-8f9c-5c85-b374-1f7e73d0822a`
  - Quote: T1110: Brute Force

## rag_003 — exact_identifier

Which ATT&CK technique name corresponds to T1078?

Expected answer: Valid Accounts.
Rationale: The pinned ATT&CK heading provides the identifier mapping.
Answerable: True; review: pending

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b33-1`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts
  - Source block IDs: `ff189459-e060-5175-9606-305270c8b3e2`
  - Quote: T1078: Valid Accounts

## rag_004 — exact_identifier

Which OWASP WSTG test identifier covers SQL injection?

Expected answer: WSTG-INPV-05.
Rationale: The source document has an explicit ID table.
Answerable: True; review: pending

- Source: `owasp_wstg_v4_2_sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `owasp_wstg_v4_2_sql_injection-b1-1`
  - Section: Testing for SQL Injection
  - Source block IDs: `5e57aec8-0467-56af-ae82-5d6a0ddc5fb1`
  - Quote: ID: WSTG-INPV-05

## rag_005 — exact_identifier

检测规则 R002 的严重程度和响应动作是什么？

Expected answer: Critical；Isolate。
Rationale: The expected row appears in the merged table; a different row must not count.
Answerable: True; review: pending

- Source: `continued_rules.pdf`; pages: 1–2; grade: 3
  - Evidence: `continued_rules-b1-1`
  - Section: Detection Rules
  - Source block IDs: `0a3d43db-7507-5175-932e-b0e4c63d7cc4`, `23a74a07-c821-5432-9917-c1bcab1862ff`
  - Quote: Rule ID: R002 / Severity: Critical / Response: Isolate

## rag_006 — semantic

Can the Windows scripting shell fetch an executable and run it without first writing it to disk?

Expected answer: Yes; PowerShell can download executables and execute them in memory.
Rationale: The description explicitly contrasts disk and in-memory execution.
Answerable: True; review: pending

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b7-1`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell
  - Source block IDs: `33fd520c-129b-5f4b-8df8-a97aacf70b18`
  - Quote: PowerShell may also be used to download and run executables from the Internet, which can be executed from disk or in memory without touching disk.

## rag_007 — semantic

Can password guessing be performed without contacting a live authentication service?

Expected answer: Yes; brute forcing can run offline against acquired credential data such as password hashes.
Rationale: The same paragraph also describes online guessing, so offline context is required.
Answerable: True; review: pending

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b21-1`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1110: Brute Force
  - Source block IDs: `4d51492c-82c9-5070-bbb3-9fdb5fbfde4f`
  - Quote: Brute forcing passwords can take place via interaction with a service that will check the validity of those credentials or offline against previously acquired credential data, such as password hashes.

## rag_008 — semantic

Why might an intruder reuse an employee account that is no longer active?

Expected answer: The original user is absent and cannot notice anomalous account activity.
Rationale: This targets the reason for inactive-account abuse, not the technique title.
Answerable: True; review: pending

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b35-1`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts
  - Source block IDs: `bb628f12-2e55-5087-9388-86597c2be15c`
  - Quote: Using these accounts may allow the adversary to evade detection, as the original account user will not be present to identify any anomalous activity taking place on their account.

## rag_009 — semantic

How can a tester infer database information when no data is returned directly?

Expected answer: Use inferential/blind SQL injection: send requests and observe database behaviour.
Rationale: The source distinguishes inference from direct data transfer.
Answerable: True; review: pending

- Source: `owasp_wstg_v4_2_sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `owasp_wstg_v4_2_sql_injection-b17-1`
  - Section: Testing for SQL Injection > Summary
  - Source block IDs: `43da13f1-0522-5462-9973-325458b7c9e8`
  - Quote: Inferential or Blind: there is no actual transfer of data, but the tester is able to reconstruct the information by sending particular requests and observing the resulting behavior of the DB Server.

## rag_010 — semantic

What kinds of observable occurrences are considered events in the NIST incident-response guidance?

Expected answer: Observable occurrences involving computing assets, including platforms, networks, services and cloud environments.
Rationale: Grounded in the actual three-page NIST excerpt, not an absent section.
Answerable: True; review: pending

- Source: `nist_sp80061r3_pp10-12.pdf`; pages: 1–1; grade: 3
  - Evidence: `nist_sp80061r3_pp10-12-b1-1`
  - Section: (none)
  - Source block IDs: `ff45e0e6-d8a0-516a-9adf-527fecaebd31`
  - Quote: Within this document, an event is any observable occurrence that involves computing assets, including physical and virtual platforms, networks, services, and cloud environments.

## rag_011 — response

暴力破解告警的本地响应清单建议采取哪些措施？

Expected answer: 封禁可疑 IP、启用 MFA、调查受影响账户。
Rationale: All three source checklist entries are required; not merely one action.
Answerable: True; review: pending

- Source: `brute_force.md`; pages: None–None; grade: 3
  - Evidence: `brute_force-b10-1`
  - Section: Brute Force Attack > Response
  - Source block IDs: `c74f8193-1c4e-505f-8635-a2ee3765eb35`
  - Quote: Block suspicious IP

- Source: `brute_force.md`; pages: None–None; grade: 3
  - Evidence: `brute_force-b11-2`
  - Section: Brute Force Attack > Response
  - Source block IDs: `e4c5acd1-6a01-5eb2-b76f-921c176f8483`
  - Quote: Enable MFA

- Source: `brute_force.md`; pages: None–None; grade: 3
  - Evidence: `brute_force-b12-3`
  - Section: Brute Force Attack > Response
  - Source block IDs: `fdc90658-40c0-5122-b255-1b934a93812b`
  - Quote: Investigate affected accounts

## rag_012 — response

According to the malware response checklist, how should compromised credentials and backups be handled?

Expected answer: Reset compromised credentials and restore systems from clean backups.
Rationale: Two separate response items supply the requested actions.
Answerable: True; review: pending

- Source: `malware.md`; pages: None–None; grade: 3
  - Evidence: `malware-b17-1`
  - Section: Malware > Response
  - Source block IDs: `cddc7cd0-ca46-5b71-9ce2-04c512eba076`
  - Quote: Reset compromised credentials

- Source: `malware.md`; pages: None–None; grade: 3
  - Evidence: `malware-b18-2`
  - Section: Malware > Response
  - Source block IDs: `192826d3-d01b-531a-b2f0-c19e1f69f940`
  - Quote: Restore systems from clean backups

## rag_013 — response

What immediate network containment action does the malware response checklist recommend?

Expected answer: Isolate affected systems from the network.
Rationale: The question is specific to the existing project malware checklist.
Answerable: True; review: pending

- Source: `malware.md`; pages: None–None; grade: 3
  - Evidence: `malware-b14-1`
  - Section: Malware > Response
  - Source block IDs: `673d2578-1560-51e1-a55a-1323de1d3798`
  - Quote: Isolate affected systems from the network

## rag_014 — response

本地 SQL 注入知识库列出了哪些预防措施？

Expected answer: 预编译语句、输入验证、最小权限。
Rationale: All three items from the local Prevention section are annotated.
Answerable: True; review: pending

- Source: `sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `sql_injection-b9-1`
  - Section: SQL Injection > Prevention
  - Source block IDs: `e13ebf1a-556b-55b7-9bf3-e89f062b4bf6`
  - Quote: Prepared statements

- Source: `sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `sql_injection-b10-2`
  - Section: SQL Injection > Prevention
  - Source block IDs: `4dfe812d-d459-533d-ae8a-6066c26ecc95`
  - Quote: Input validation

- Source: `sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `sql_injection-b11-3`
  - Section: SQL Injection > Prevention
  - Source block IDs: `0c38339f-b554-59f9-a5cd-c230f13ef0d7`
  - Quote: Least privilege

## rag_015 — response

Why should lessons learned during incident response be shared before recovery has finished?

Expected answer: Modern incidents are frequent, complex and lengthy; lessons should be shared as identified to support continuous improvement.
Rationale: The final paragraph of the excerpt directly states the timing rationale.
Answerable: True; review: pending

- Source: `nist_sp80061r3_pp10-12.pdf`; pages: 3–3; grade: 3
  - Evidence: `nist_sp80061r3_pp10-12-b38-1`
  - Section: 2.1. Incident Response Life Cycle Model > Containment
  - Source block IDs: `f6162960-05d9-52ae-9d47-a71be9bf79ae`
  - Quote: The lessons learned during incident response should often be shared as soon as they are identified, not delayed until after recovery concludes.

## rag_016 — tables_steps

For detection rule R004, what severity and response are specified?

Expected answer: High; Block.
Rationale: This row originated on the second page of the continued table.
Answerable: True; review: pending

- Source: `continued_rules.pdf`; pages: 1–2; grade: 3
  - Evidence: `continued_rules-b1-1`
  - Section: Detection Rules
  - Source block IDs: `0a3d43db-7507-5175-932e-b0e4c63d7cc4`, `23a74a07-c821-5432-9917-c1bcab1862ff`
  - Quote: Rule ID: R004 / Severity: High / Response: Block

## rag_017 — tables_steps

Which rule has Medium severity and what response does it require?

Expected answer: R003; Review.
Rationale: Requires the relevant table row rather than shared table provenance.
Answerable: True; review: pending

- Source: `continued_rules.pdf`; pages: 1–2; grade: 3
  - Evidence: `continued_rules-b1-1`
  - Section: Detection Rules
  - Source block IDs: `0a3d43db-7507-5175-932e-b0e4c63d7cc4`, `23a74a07-c821-5432-9917-c1bcab1862ff`
  - Quote: Rule ID: R003 / Severity: Medium / Response: Review

## rag_018 — tables_steps

What are the three numbered actions in the response checklist, in order?

Expected answer: Check firewall configuration; collect authentication logs; isolate affected hosts.
Rationale: Operational steps should remain body text and all three must be retrievable.
Answerable: True; review: pending

- Source: `numbered_steps.docx`; pages: None–None; grade: 3
  - Evidence: `numbered_steps-b1-1`
  - Section: Response checklist
  - Source block IDs: `34337ceb-b993-5c48-af5a-98498100cf5a`
  - Quote: 1. Check firewall configuration

- Source: `numbered_steps.docx`; pages: None–None; grade: 3
  - Evidence: `numbered_steps-b2-2`
  - Section: Response checklist
  - Source block IDs: `aec40a56-e98b-5dcf-943a-e3c9512395d8`
  - Quote: 2. Collect authentication logs

- Source: `numbered_steps.docx`; pages: None–None; grade: 3
  - Evidence: `numbered_steps-b3-3`
  - Section: Response checklist
  - Source block IDs: `4c284a64-54ca-5487-a6c4-5d69aa0e3c81`
  - Quote: 3. Isolate affected hosts

## rag_019 — tables_steps

What does the authentication rule do after checking events in the cross-page investigation note?

Expected answer: It correlates failed login attempts across accounts.
Rationale: The relevant sentence spans both physical pages, so the label retains both source IDs.
Answerable: True; review: pending

- Source: `sentence_continuation.pdf`; pages: 1–2; grade: 3
  - Evidence: `sentence_continuation-b1-1`
  - Section: Authentication investigation
  - Source block IDs: `a29b1520-dbe7-59b7-8f00-c089f5767197`
  - Quote: The authentication rule checks events, then correlates failed login attempts across accounts.

## rag_020 — tables_steps

When enumerating SQL-injection inputs, should hidden POST fields, HTTP headers and cookies be included?

Expected answer: Yes; test the input fields separately and consider headers and cookies.
Rationale: The instruction is in the OWASP Detection Techniques section.
Answerable: True; review: pending

- Source: `owasp_wstg_v4_2_sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `owasp_wstg_v4_2_sql_injection-b34-1`
  - Section: Testing for SQL Injection > How to Test > Detection Techniques
  - Source block IDs: `2a3b25de-590d-55a4-a251-2cfef4274def`
  - Quote: The tester has to make a list of all input fields whose values could be used in crafting a SQL query, including the hidden fields of POST requests and then test them separately, trying to interfere with the query and to generate an error. Consider also HTTP headers and Cookies.

## rag_021 — context

How do inband, out-of-band and blind SQL injection differ in the way information is obtained?

Expected answer: Inband uses the injection channel; out-of-band uses another channel; blind infers from behaviour without direct data transfer.
Rationale: Requires three distinct source definitions.
Answerable: True; review: pending

- Source: `owasp_wstg_v4_2_sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `owasp_wstg_v4_2_sql_injection-b15-1`
  - Section: Testing for SQL Injection > Summary
  - Source block IDs: `ca6280cf-0816-550f-8857-089ee53e158d`
  - Quote: Inband: data is extracted using the same channel that is used to inject the SQL code. This is the most straightforward kind of attack, in which the retrieved data is presented directly in the application web page.

- Source: `owasp_wstg_v4_2_sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `owasp_wstg_v4_2_sql_injection-b16-2`
  - Section: Testing for SQL Injection > Summary
  - Source block IDs: `f2a22a75-f5e5-51f3-a548-4d7639e958b8`
  - Quote: Out-of-band: data is retrieved using a different channel (e.g., an email with the results of the query is generated and sent to the tester).

- Source: `owasp_wstg_v4_2_sql_injection.md`; pages: None–None; grade: 3
  - Evidence: `owasp_wstg_v4_2_sql_injection-b17-3`
  - Section: Testing for SQL Injection > Summary
  - Source block IDs: `43da13f1-0522-5462-9973-325458b7c9e8`
  - Quote: Inferential or Blind: there is no actual transfer of data, but the tester is able to reconstruct the information by sending particular requests and observing the resulting behavior of the DB Server.

## rag_022 — context

Why does NIST Rev. 3 emphasize cybersecurity risk management instead of maintaining every detailed response procedure?

Expected answer: Detailed procedures vary and change too often for one static publication; the revision focuses on all CSF 2.0 Functions.
Rationale: Two explicit claims in the scope paragraph must be supported.
Answerable: True; review: pending

- Source: `nist_sp80061r3_pp10-12.pdf`; pages: 2–2; grade: 3
  - Evidence: `nist_sp80061r3_pp10-12-b14-1`
  - Section: A cybersecurity incident (or simply incident) is
  - Source block IDs: `4a0e88f0-2723-5bcc-83f6-e62e853990cc`
  - Quote: Because the details of how to perform incident response activities change so often and vary so much across technologies, environments, and organizations, it is no longer feasible to capture and maintain that information in a single static publication.

- Source: `nist_sp80061r3_pp10-12.pdf`; pages: 2–2; grade: 3
  - Evidence: `nist_sp80061r3_pp10-12-b14-2`
  - Section: A cybersecurity incident (or simply incident) is
  - Source block IDs: `4a0e88f0-2723-5bcc-83f6-e62e853990cc`
  - Quote: Instead, this version focuses on improving cybersecurity risk management for all of the NIST Cybersecurity Framework (CSF) 2.0 Functions [CSF2.0] to better support an organization's incident response capabilities.

## rag_023 — context

For remote PowerShell command execution, which cmdlet is mentioned and what permission prerequisite applies?

Expected answer: Invoke-Command; administrator permissions are required to connect to remote systems.
Rationale: The Markdown parser splits inline code from surrounding text; both pieces are needed.
Answerable: True; review: pending

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b5-1`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell
  - Source block IDs: `a3d32a81-9c33-58d7-bb87-3e48ded23c83`
  - Quote: Invoke-Command

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b6-2`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell
  - Source block IDs: `05d2351c-251b-5dc8-9104-11f43821c958`
  - Quote: cmdlet which runs a command locally or on a remote computer (though administrator permissions are required to use PowerShell to connect to remote systems).

## rag_024 — context

What cross-account authentication indicators and matching response actions are listed in the brute-force guide?

Expected answer: Same source IP attacking multiple accounts/high-frequency failures; block suspicious IP, enable MFA and investigate accounts.
Rationale: Spans Detection and Response sections, so one parent is not sufficient.
Answerable: True; review: pending

- Source: `brute_force.md`; pages: None–None; grade: 3
  - Evidence: `brute_force-b6-1`
  - Section: Brute Force Attack > Detection
  - Source block IDs: `efffc5d5-51e8-5756-bb79-b4c0dfc8bc6b`
  - Quote: Same source IP attacking multiple accounts

- Source: `brute_force.md`; pages: None–None; grade: 3
  - Evidence: `brute_force-b7-2`
  - Section: Brute Force Attack > Detection
  - Source block IDs: `6423c98c-3b78-50dc-9d12-d5d4dad460e9`
  - Quote: High frequency authentication failures

- Source: `brute_force.md`; pages: None–None; grade: 3
  - Evidence: `brute_force-b10-3`
  - Section: Brute Force Attack > Response
  - Source block IDs: `c74f8193-1c4e-505f-8635-a2ee3765eb35`
  - Quote: Block suspicious IP

- Source: `brute_force.md`; pages: None–None; grade: 3
  - Evidence: `brute_force-b11-4`
  - Section: Brute Force Attack > Response
  - Source block IDs: `e4c5acd1-6a01-5eb2-b76f-921c176f8483`
  - Quote: Enable MFA

- Source: `brute_force.md`; pages: None–None; grade: 3
  - Evidence: `brute_force-b12-5`
  - Section: Brute Force Attack > Response
  - Source block IDs: `fdc90658-40c0-5122-b255-1b934a93812b`
  - Quote: Investigate affected accounts

## rag_025 — context

What does the valid-accounts description say about both bypassing access controls and moving across account types?

Expected answer: Compromised credentials can bypass controls; overlapping local, domain and cloud permissions can enable privilege escalation.
Rationale: Two paragraphs describe access-control bypass and cross-account privilege concerns.
Answerable: True; review: pending

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b34-1`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts
  - Source block IDs: `9df49cee-b541-5e50-a1db-22159ec3bf17`
  - Quote: Compromised credentials may be used to bypass access controls

- Source: `mitre_attack_v17_1.md`; pages: None–None; grade: 3
  - Evidence: `mitre_attack_v17_1-b36-2`
  - Section: MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts
  - Source block IDs: `b96b8f17-37a3-5d39-b01e-c367ec19ce11`
  - Quote: The overlap of permissions for local, domain, and cloud accounts across a network of systems is of concern because the adversary may be able to pivot across accounts and systems to reach a high level of access (i.e., domain or enterprise administrator) to bypass access controls set within the enterprise.(Citation: TechNet Credential Theft)

## rag_026 — unanswerable

What is the exact production API key for the fictional Acme SOC deployment?

Expected answer: Insufficient evidence in this corpus.
Rationale: The frozen corpus contains public guidance and synthetic examples, no private deployment credentials.
Answerable: False; review: pending

## rag_027 — unanswerable

What indicators of compromise are documented for the fictional CVE-2099-99999?

Expected answer: Insufficient evidence in this corpus.
Rationale: This fictional identifier and its indicators do not occur in the frozen corpus.
Answerable: False; review: pending

## rag_028 — unanswerable

在 2026-10-31 这次告警中，攻击者实际登录了哪些生产账户？

Expected answer: Insufficient evidence in this corpus.
Rationale: The corpus is reference guidance, not observed event telemetry for a dated production incident.
Answerable: False; review: pending

## rag_029 — unanswerable

Which vendor firmware command disables the fictional QuantumShield X900 audit engine?

Expected answer: Insufficient evidence in this corpus.
Rationale: No QuantumShield X900 vendor manual or commands are included.
Answerable: False; review: pending

## rag_030 — unanswerable

What exact financial loss did the fictional ACME incident cause on 2026-10-31?

Expected answer: Insufficient evidence in this corpus.
Rationale: No ACME incident records or financial-loss data are in the corpus.
Answerable: False; review: pending

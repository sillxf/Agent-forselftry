# 30 题来源审查与人工复核单

**来源核对由 AI 完成，不等于人工相关性批准。所有待审核状态保持不变。**

数据集：`rag-benchmark-v0.3.1-structure-corrected-candidate`。JSONL 是标签的唯一事实来源。
一个 evidence_id 表示一项事实；alternatives 是相同事实的 OR 位置，不增加 Recall 分母。
确认问题、答案、所有有效来源、分级、实际页码/章节后，由真实审核人填写 reviewer 并批准。

## rag_001 — exact_identifier

T1059.001 refers to which Windows scripting environment?

参考答案：PowerShell.
依据：The selected ATT&CK technique heading gives the identifier and name.
来源审查：固定 ATT&CK T1059.001 标题直接给出 PowerShell 名称；未引用在线最新版。
人工状态：`pending`；审核人：`None`

### 事实 `mitre_attack_v17_1-b1-1`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`c2440acc-92b4-55a1-8358-fc947f7295d9`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell
  - 原文：T1059.001: PowerShell

- [ ] 人工确认：确认标题正文证据口径，是否另行评价章节元数据中的答案。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_002 — exact_identifier

What technique is assigned the ATT&CK identifier T1110?

参考答案：Brute Force.
依据：The pinned ATT&CK heading provides the identifier mapping.
来源审查：T1110 与 Brute Force 的对应关系有直接标题证据；排名第一的文档总标题不包含该对应关系。
人工状态：`pending`；审核人：`None`

### 事实 `mitre_attack_v17_1-b20-1`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`a48dc3aa-8f9c-5c85-b374-1f7e73d0822a`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1110: Brute Force
  - 原文：T1110: Brute Force

- [ ] 人工确认：核准“空泛总标题命中”属于排序失败，而非标注遗漏。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_003 — exact_identifier

Which ATT&CK technique name corresponds to T1078?

参考答案：Valid Accounts.
依据：The pinned ATT&CK heading provides the identifier mapping.
来源审查：T1078 标题直接给出 Valid Accounts；部分 Child 正文未重现标题，但 section_path 已含答案。
人工状态：`pending`；审核人：`None`

### 事实 `mitre_attack_v17_1-b33-1`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`ff189459-e060-5175-9606-305270c8b3e2`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts
  - 原文：T1078: Valid Accounts

- [ ] 人工确认：决定是否保留当前“只计正文证据”的统一口径；不要仅为本题放宽。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_004 — exact_identifier

Which OWASP WSTG test identifier covers SQL injection?

参考答案：WSTG-INPV-05.
依据：The source document has an explicit ID table.
来源审查：WSTG-INPV-05 位于文件开头 ID 表中；命中文档标题并不能单独回答编号。
人工状态：`pending`；审核人：`None`

### 事实 `owasp_wstg_v4_2_sql_injection-b1-1`（grade=3）

- 主位置：`owasp_wstg_v4_2_sql_injection.md`；索引页范围：None–None
  - Document ID：`2875edd4308dfe6d3c746f3d14d08c877916344c990cbacfdec12fcdcd272a25`
  - 原始 Block：`5e57aec8-0467-56af-ae82-5d6a0ddc5fb1`
  - 解析章节：Testing for SQL Injection
  - 原文：ID: WSTG-INPV-05

- [ ] 人工确认：确认 Child 缺失而 Parent 命中的情况单独报告，不合并两层 Recall。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_005 — exact_identifier

检测规则 R002 的严重程度和响应动作是什么？

参考答案：Critical；Isolate。
依据：The expected row appears in the merged table; a different row must not count.
来源审查：R002 / Critical / Isolate 是独立表格规则，事实 ID 改为 continued_rules-r002；同表 R003、R004 不等价。
人工状态：`pending`；审核人：`None`

本轮事实检查：R002 / Critical / Isolate 是独立表格规则，事实 ID 改为 continued_rules-r002；同表 R003、R004 不等价。
所需证据范围：`reference_knowledge`

### 事实 `continued_rules-r002`（grade=3）

- 主位置：`continued_rules.pdf`；索引页范围：1–2
  - Document ID：`87510542255f99549117a1506c95237fab2294df0f2ca0288eb3f7c48c6979cd`
  - 原始 Block：`0a3d43db-7507-5175-932e-b0e4c63d7cc4`, `23a74a07-c821-5432-9917-c1bcab1862ff`
  - 解析章节：Detection Rules
  - 原文：Rule ID: R002 / Severity: Critical / Response: Isolate

- [ ] 人工确认：确认页范围表示合并证据范围，不伪造为精确行级页码。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_006 — semantic

Can the Windows scripting shell fetch an executable and run it without first writing it to disk?

参考答案：Yes; PowerShell can download executables and execute them in memory.
依据：The description explicitly contrasts disk and in-memory execution.
来源审查：PowerShell 描述明确允许下载后从内存执行，不需首先写入磁盘。
人工状态：`pending`；审核人：`None`

### 事实 `mitre_attack_v17_1-b7-1`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`33fd520c-129b-5f4b-8df8-a97aacf70b18`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell
  - 原文：PowerShell may also be used to download and run executables from the Internet, which can be executed from disk or in memory without touching disk.

- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_007 — semantic

Can password guessing be performed without contacting a live authentication service?

参考答案：Yes; brute forcing can run offline against acquired credential data such as password hashes.
依据：The anchor isolates the offline-credential clause; surrounding online-guessing details are not required to answer.
来源审查：离线口令猜测与 password hashes 在同一原文句子中；缩短 anchor 去掉无关在线验证背景。
人工状态：`pending`；审核人：`None`

### 事实 `mitre_attack_v17_1-b21-1`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`4d51492c-82c9-5070-bbb3-9fdb5fbfde4f`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1110: Brute Force
  - 原文：offline against previously acquired credential data, such as password hashes.

- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_008 — semantic

Why might an intruder reuse an employee account that is no longer active?

参考答案：The original user is absent and cannot notice anomalous account activity.
依据：The anchor retains the reason inactive accounts can evade their original users' detection, without unrelated background.
来源审查：停用账户原使用者无法发现异常是原文明示的规避检测理由；保留完整因果片段。
人工状态：`pending`；审核人：`None`

### 事实 `mitre_attack_v17_1-b35-1`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`bb628f12-2e55-5087-9388-86597c2be15c`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts
  - 原文：the original account user will not be present to identify any anomalous activity taking place on their account.

- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_009 — semantic

How can a tester infer database information when no data is returned directly?

参考答案：Use inferential/blind SQL injection: send requests and observe database behaviour.
依据：The source distinguishes inference from direct data transfer.
来源审查：Summary 的 Blind 定义完整支持无直接数据传输、通过请求/行为重构信息。
人工状态：`pending`；审核人：`None`

### 事实 `owasp_wstg_v4_2_sql_injection-b17-1`（grade=3）

- 主位置：`owasp_wstg_v4_2_sql_injection.md`；索引页范围：None–None
  - Document ID：`2875edd4308dfe6d3c746f3d14d08c877916344c990cbacfdec12fcdcd272a25`
  - 原始 Block：`43da13f1-0522-5462-9973-325458b7c9e8`
  - 解析章节：Testing for SQL Injection > Summary
  - 原文：Inferential or Blind: there is no actual transfer of data, but the tester is able to reconstruct the information by sending particular requests and observing the resulting behavior of the DB Server.

- [ ] 人工确认：判断 Boolean/Time Delay 后续实例是否应作为额外替代证据；目前不把含 blind 一词的任意片段都算正确。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_010 — semantic

What kinds of observable occurrences are considered events in the NIST incident-response guidance?

参考答案：Observable occurrences involving computing assets, including platforms, networks, services and cloud environments.
依据：Grounded in the actual three-page NIST excerpt, not an absent section.
来源审查：NIST 节选物理第 1 页支持事件定义；不是原 PDF 的物理第 1 页。
人工状态：`pending`；审核人：`None`

### 事实 `nist_sp80061r3_pp10-12-b1-1`（grade=3）

- 主位置：`nist_sp80061r3_pp10-12.pdf`；索引页范围：1–1
  - Document ID：`dc95e150e756524e3bc38e81b5be7e2e912135c1633aea9f885667fe521e4830`
  - 原始 Block：`ff45e0e6-d8a0-516a-9adf-527fecaebd31`
  - 解析章节：1. Introduction
  - 原文：Within this document, an event is any observable occurrence that involves computing assets, including physical and virtual platforms, networks, services, and cloud environments.

- [ ] 人工确认：核对原始标题 1. Introduction；解析得到的 section_path 不等于可靠的原始层级。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_011 — response

暴力破解告警的本地响应清单建议采取哪些措施？

参考答案：封禁可疑 IP、启用 MFA、调查受影响账户。
依据：All three source checklist entries are required; not merely one action.
来源审查：本地 brute_force.md Response 的三个动作均已标注；保留中文问题与英文语料，不改写为更容易检索的问法。
人工状态：`pending`；审核人：`None`

本轮事实检查：问题问完整本地处置清单：三项动作均必要；冻结 brute_force.md 只有英文处置清单，无等价中文位置。不凭外部翻译虚构 alternatives。
所需证据范围：`reference_knowledge`

### 事实 `brute_force-b10-1`（grade=3）

- 主位置：`brute_force.md`；索引页范围：None–None
  - Document ID：`219450061de1a4e313195418629a3092055a4129f1ec565cc80cd72d63aa65aa`
  - 原始 Block：`c74f8193-1c4e-505f-8635-a2ee3765eb35`
  - 解析章节：Brute Force Attack > Response
  - 原文：Block suspicious IP

### 事实 `brute_force-b11-2`（grade=3）

- 主位置：`brute_force.md`；索引页范围：None–None
  - Document ID：`219450061de1a4e313195418629a3092055a4129f1ec565cc80cd72d63aa65aa`
  - 原始 Block：`e4c5acd1-6a01-5eb2-b76f-921c176f8483`
  - 解析章节：Brute Force Attack > Response
  - 原文：Enable MFA

### 事实 `brute_force-b12-3`（grade=3）

- 主位置：`brute_force.md`；索引页范围：None–None
  - Document ID：`219450061de1a4e313195418629a3092055a4129f1ec565cc80cd72d63aa65aa`
  - 原始 Block：`fdc90658-40c0-5122-b255-1b934a93812b`
  - 解析章节：Brute Force Attack > Response
  - 原文：Investigate affected accounts

- [ ] 人工确认：确认跨语言查询是预期使用场景；先核准标签，再解释检索失败。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_012 — response

According to the malware response checklist, how should compromised credentials and backups be handled?

参考答案：Reset compromised credentials and restore systems from clean backups.
依据：Two separate response items supply the requested actions.
来源审查：malware.md 直接列出重置受损凭证与从干净备份恢复两项措施。
人工状态：`pending`；审核人：`None`

本轮事实检查：问题同时询问凭据和备份，两项独立动作都必要；不添加隔离、扫描等未问及的清单项。属于一般处置知识，不代表当前凭据确实失陷。
所需证据范围：`reference_knowledge`

### 事实 `malware-b17-1`（grade=3）

- 主位置：`malware.md`；索引页范围：None–None
  - Document ID：`3e305e96177e5e472096791b6977d6a6ca821cbe1e478eba62b47492cd5e37fa`
  - 原始 Block：`cddc7cd0-ca46-5b71-9ce2-04c512eba076`
  - 解析章节：Malware > Response
  - 原文：Reset compromised credentials

### 事实 `malware-b18-2`（grade=3）

- 主位置：`malware.md`；索引页范围：None–None
  - Document ID：`3e305e96177e5e472096791b6977d6a6ca821cbe1e478eba62b47492cd5e37fa`
  - 原始 Block：`192826d3-d01b-531a-b2f0-c19e1f69f940`
  - 解析章节：Malware > Response
  - 原文：Restore systems from clean backups

- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_013 — response

What immediate network containment action does the malware response checklist recommend?

参考答案：Isolate affected systems from the network.
依据：The question is specific to the existing project malware checklist.
来源审查：malware.md 的隔离步骤是指定来源；普通响应清单中的同名隔离动作不自动视为同一语境证据。
人工状态：`pending`；审核人：`None`

### 事实 `malware-b14-1`（grade=3）

- 主位置：`malware.md`；索引页范围：None–None
  - Document ID：`3e305e96177e5e472096791b6977d6a6ca821cbe1e478eba62b47492cd5e37fa`
  - 原始 Block：`673d2578-1560-51e1-a55a-1323de1d3798`
  - 解析章节：Malware > Response
  - 原文：Isolate affected systems from the network

- [ ] 人工确认：确认提问中的 malware checklist 来源约束是否符合实际用户需求。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_014 — response

本地 SQL 注入知识库列出了哪些预防措施？

参考答案：预编译语句、输入验证、最小权限。
依据：All three items from the local Prevention section are annotated.
来源审查：本地 SQL 注入文件列出 prepared statements、input validation、least privilege；链接到其他指南不等于其内容已入库。
人工状态：`pending`；审核人：`None`

本轮事实检查：问题问完整本地预防清单：预编译语句、输入验证、最小权限均必要。冻结 sql_injection.md 无中文重复条目，不虚构 alternatives。
所需证据范围：`reference_knowledge`

### 事实 `sql_injection-b9-1`（grade=3）

- 主位置：`sql_injection.md`；索引页范围：None–None
  - Document ID：`43df01ed52ac2c6a53b1c3bfd828f33e26dba7f78724daeb4aeb003860b73943`
  - 原始 Block：`e13ebf1a-556b-55b7-9bf3-e89f062b4bf6`
  - 解析章节：SQL Injection > Prevention
  - 原文：Prepared statements

### 事实 `sql_injection-b10-2`（grade=3）

- 主位置：`sql_injection.md`；索引页范围：None–None
  - Document ID：`43df01ed52ac2c6a53b1c3bfd828f33e26dba7f78724daeb4aeb003860b73943`
  - 原始 Block：`4dfe812d-d459-533d-ae8a-6066c26ecc95`
  - 解析章节：SQL Injection > Prevention
  - 原文：Input validation

### 事实 `sql_injection-b11-3`（grade=3）

- 主位置：`sql_injection.md`；索引页范围：None–None
  - Document ID：`43df01ed52ac2c6a53b1c3bfd828f33e26dba7f78724daeb4aeb003860b73943`
  - 原始 Block：`0c38339f-b554-59f9-a5cd-c230f13ef0d7`
  - 解析章节：SQL Injection > Prevention
  - 原文：Least privilege

- [ ] 人工确认：确认中文查询与指定本地来源约束；不可用外部未入库知识补标签。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_015 — response

Why should lessons learned during incident response be shared before recovery has finished?

参考答案：Modern incidents are frequent, complex and lengthy; lessons should be shared as identified to support continuous improvement.
依据：The original timing claim is preserved. Added anchors explain modern incident complexity and the need for continuous improvement, rather than treating the timing recommendation alone as its own explanation.
来源审查：旧引用只重复“及时分享”的要求，不能完整解释原因；保留该时机主张，补充现代事件复杂性与持续改进两项解释性事实。
人工状态：`pending`；审核人：`None`

本轮事实检查：保留三个事实：及时共享的建议、现代事件恢复的复杂性和时长、持续改进的必要性。后两项是 why 的理由，第一项是被解释的建议；请人工确认三者是否均应计入召回分母，未为提高 Recall 删除。
所需证据范围：`reference_knowledge`

### 事实 `nist_sp80061r3_pp10-12-b38-1`（grade=3）

- 主位置：`nist_sp80061r3_pp10-12.pdf`；索引页范围：3–3
  - Document ID：`dc95e150e756524e3bc38e81b5be7e2e912135c1633aea9f885667fe521e4830`
  - 原始 Block：`f6162960-05d9-52ae-9d47-a71be9bf79ae`
  - 解析章节：2. Incident Response as Part of Cybersecurity Risk Management > 2.1. Incident Response Life Cycle Model
  - 原文：The lessons learned during incident response should often be shared as soon as they are identified, not delayed until after recovery concludes.

### 事实 `nist-modern-incident-complexity`（grade=3）

- 主位置：`nist_sp80061r3_pp10-12.pdf`；索引页范围：3–3
  - Document ID：`dc95e150e756524e3bc38e81b5be7e2e912135c1633aea9f885667fe521e4830`
  - 原始 Block：`f6162960-05d9-52ae-9d47-a71be9bf79ae`
  - 解析章节：2. Incident Response as Part of Cybersecurity Risk Management > 2.1. Incident Response Life Cycle Model
  - 原文：Today, incidents occur frequently and cause far more damage. Recovering from them often takes weeks or months due to their breadth, complexity, and dynamic nature.

### 事实 `nist-continuous-improvement`（grade=3）

- 主位置：`nist_sp80061r3_pp10-12.pdf`；索引页范围：3–3
  - Document ID：`dc95e150e756524e3bc38e81b5be7e2e912135c1633aea9f885667fe521e4830`
  - 原始 Block：`f6162960-05d9-52ae-9d47-a71be9bf79ae`
  - 解析章节：2. Incident Response as Part of Cybersecurity Risk Management > 2.1. Incident Response Life Cycle Model
  - 原文：Continuous improvement is increasingly necessary for all facets of cybersecurity risk management in order to keep up with modern threats.

- [ ] 人工确认：确认时机主张及两项原因是否均为本题必要事实，并核准分级相关性；不能把图中的旧版生命周期结论当作现代建议。
- [ ] 人工确认：确认 why 问题的三个事实是否均为必要答案内容；此次未删除任何事实。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_016 — tables_steps

For detection rule R004, what severity and response are specified?

参考答案：High; Block.
依据：This row originated on the second page of the continued table.
来源审查：R004 / High / Block 是独立表格规则，事实 ID 改为 continued_rules-r004；共同表格来源不能共用事实 ID。
人工状态：`pending`；审核人：`None`

本轮事实检查：R004 / High / Block 是独立表格规则，事实 ID 改为 continued_rules-r004；共同表格来源不能共用事实 ID。
所需证据范围：`reference_knowledge`

### 事实 `continued_rules-r004`（grade=3）

- 主位置：`continued_rules.pdf`；索引页范围：1–2
  - Document ID：`87510542255f99549117a1506c95237fab2294df0f2ca0288eb3f7c48c6979cd`
  - 原始 Block：`0a3d43db-7507-5175-932e-b0e4c63d7cc4`, `23a74a07-c821-5432-9917-c1bcab1862ff`
  - 解析章节：Detection Rules
  - 原文：Rule ID: R004 / Severity: High / Response: Block

- [ ] 人工确认：是否后续需要行级页码：本轮不把合并页范围改装成精确行定位。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_017 — tables_steps

Which rule has Medium severity and what response does it require?

参考答案：R003; Review.
依据：Requires the relevant table row rather than shared table provenance.
来源审查：R003 / Medium / Review 是独立表格规则，事实 ID 改为 continued_rules-r003；保留原问答和完整行证据。
人工状态：`pending`；审核人：`None`

本轮事实检查：R003 / Medium / Review 是独立表格规则，事实 ID 改为 continued_rules-r003；保留原问答和完整行证据。
所需证据范围：`reference_knowledge`

### 事实 `continued_rules-r003`（grade=3）

- 主位置：`continued_rules.pdf`；索引页范围：1–2
  - Document ID：`87510542255f99549117a1506c95237fab2294df0f2ca0288eb3f7c48c6979cd`
  - 原始 Block：`0a3d43db-7507-5175-932e-b0e4c63d7cc4`, `23a74a07-c821-5432-9917-c1bcab1862ff`
  - 解析章节：Detection Rules
  - 原文：Rule ID: R003 / Severity: Medium / Response: Review

- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_018 — tables_steps

What are the three numbered actions in the response checklist, in order?

参考答案：Check firewall configuration; collect authentication logs; isolate affected hosts.
依据：The checklist repeats the same three ordered actions in English and Chinese. Each translated item is an alternative location for one required action, not a fourth/fifth/sixth fact.
来源审查：同一 DOCX 的中英文编号列表重复相同三步；新增三个中文替代位置，每个事实仍只计一次。
人工状态：`pending`；审核人：`None`

本轮事实检查：三项有序动作；中英各一处为同一动作的 OR 位置，不是六项必要事实。
所需证据范围：`reference_knowledge`

### 事实 `numbered_steps-b1-1`（grade=3）

- 主位置：`numbered_steps.docx`；索引页范围：None–None
  - Document ID：`d2dec7fde7d94f12b6cec329a37a41be2664a9aadea8a10760c5b4c9018ef314`
  - 原始 Block：`34337ceb-b993-5c48-af5a-98498100cf5a`
  - 解析章节：Response checklist
  - 原文：1. Check firewall configuration

- 同义替代位置（OR）：`numbered_steps.docx`；索引页范围：None–None
  - Document ID：`d2dec7fde7d94f12b6cec329a37a41be2664a9aadea8a10760c5b4c9018ef314`
  - 原始 Block：`0399ed62-9955-5a35-9f8a-1775a5ca6523`
  - 解析章节：Response checklist
  - 原文：1. 检查防火墙配置

### 事实 `numbered_steps-b2-2`（grade=3）

- 主位置：`numbered_steps.docx`；索引页范围：None–None
  - Document ID：`d2dec7fde7d94f12b6cec329a37a41be2664a9aadea8a10760c5b4c9018ef314`
  - 原始 Block：`aec40a56-e98b-5dcf-943a-e3c9512395d8`
  - 解析章节：Response checklist
  - 原文：2. Collect authentication logs

- 同义替代位置（OR）：`numbered_steps.docx`；索引页范围：None–None
  - Document ID：`d2dec7fde7d94f12b6cec329a37a41be2664a9aadea8a10760c5b4c9018ef314`
  - 原始 Block：`1ab919e2-3620-5597-9e98-b8b94a223c6d`
  - 解析章节：Response checklist
  - 原文：2. 收集认证日志

### 事实 `numbered_steps-b3-3`（grade=3）

- 主位置：`numbered_steps.docx`；索引页范围：None–None
  - Document ID：`d2dec7fde7d94f12b6cec329a37a41be2664a9aadea8a10760c5b4c9018ef314`
  - 原始 Block：`4c284a64-54ca-5487-a6c4-5d69aa0e3c81`
  - 解析章节：Response checklist
  - 原文：3. Isolate affected hosts

- 同义替代位置（OR）：`numbered_steps.docx`；索引页范围：None–None
  - Document ID：`d2dec7fde7d94f12b6cec329a37a41be2664a9aadea8a10760c5b4c9018ef314`
  - 原始 Block：`a390c03e-eeaa-5e65-9e46-831ddbfbd5ae`
  - 解析章节：Response checklist
  - 原文：3. 隔离受影响主机

- [ ] 人工确认：核准中英文语义对应与顺序；不能要求必须同时召回两种语言版本。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_019 — tables_steps

What does the authentication rule do after checking events in the cross-page investigation note?

参考答案：It correlates failed login attempts across accounts.
依据：The relevant sentence spans both physical pages, so the label retains both source IDs.
来源审查：两页续句连接后完整表达检查事件再关联跨账户失败登录；源 ID 和页范围均保留。
人工状态：`pending`；审核人：`None`

### 事实 `sentence_continuation-b1-1`（grade=3）

- 主位置：`sentence_continuation.pdf`；索引页范围：1–2
  - Document ID：`f6a0fa52f99b5e686bbfd5b355af7e908f562705a6f8895a01a2c2ce0c46a4ca`
  - 原始 Block：`a29b1520-dbe7-59b7-8f00-c089f5767197`
  - 解析章节：Authentication investigation
  - 原文：The authentication rule checks events, then correlates failed login attempts across accounts.

- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_020 — tables_steps

When enumerating SQL-injection inputs, should hidden POST fields, HTTP headers and cookies be included?

参考答案：Yes; test the input fields separately and consider headers and cookies.
依据：The instruction is in the OWASP Detection Techniques section.
来源审查：OWASP Detection Techniques 原文明确要求包含 hidden POST、HTTP headers、Cookies；完整片段在当前 Child 中可定位。
人工状态：`pending`；审核人：`None`

### 事实 `owasp_wstg_v4_2_sql_injection-b34-1`（grade=3）

- 主位置：`owasp_wstg_v4_2_sql_injection.md`；索引页范围：None–None
  - Document ID：`2875edd4308dfe6d3c746f3d14d08c877916344c990cbacfdec12fcdcd272a25`
  - 原始 Block：`2a3b25de-590d-55a4-a251-2cfef4274def`
  - 解析章节：Testing for SQL Injection > How to Test > Detection Techniques
  - 原文：The tester has to make a list of all input fields whose values could be used in crafting a SQL query, including the hidden fields of POST requests and then test them separately, trying to interfere with the query and to generate an error. Consider also HTTP headers and Cookies.

- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_021 — context

How do inband, out-of-band and blind SQL injection differ in the way information is obtained?

参考答案：Inband uses the injection channel; out-of-band uses another channel; blind infers from behaviour without direct data transfer.
依据：Three channel definitions are separate facts. The later out-of-band technique definition supports the same out-of-band fact and is an OR alternative, not an additional requirement.
来源审查：三类信息获取方式定义均有来源；后面的 Out-of-band technique 描述是相同事实的另一位置，已作为 OR 替代。
人工状态：`pending`；审核人：`None`

本轮事实检查：三个独立 SQL 注入信息通道；两个英文 out-of-band 定义是同一事实的替代位置，不是中英翻译，也不是额外第四项。
所需证据范围：`reference_knowledge`

### 事实 `owasp_wstg_v4_2_sql_injection-b15-1`（grade=3）

- 主位置：`owasp_wstg_v4_2_sql_injection.md`；索引页范围：None–None
  - Document ID：`2875edd4308dfe6d3c746f3d14d08c877916344c990cbacfdec12fcdcd272a25`
  - 原始 Block：`ca6280cf-0816-550f-8857-089ee53e158d`
  - 解析章节：Testing for SQL Injection > Summary
  - 原文：Inband: data is extracted using the same channel that is used to inject the SQL code.

### 事实 `owasp_wstg_v4_2_sql_injection-b16-2`（grade=3）

- 主位置：`owasp_wstg_v4_2_sql_injection.md`；索引页范围：None–None
  - Document ID：`2875edd4308dfe6d3c746f3d14d08c877916344c990cbacfdec12fcdcd272a25`
  - 原始 Block：`f2a22a75-f5e5-51f3-a548-4d7639e958b8`
  - 解析章节：Testing for SQL Injection > Summary
  - 原文：Out-of-band: data is retrieved using a different channel

- 同义替代位置（OR）：`owasp_wstg_v4_2_sql_injection.md`；索引页范围：None–None
  - Document ID：`2875edd4308dfe6d3c746f3d14d08c877916344c990cbacfdec12fcdcd272a25`
  - 原始 Block：`27bb783b-3793-5506-8d5a-98d5e9581fc4`
  - 解析章节：Testing for SQL Injection > Summary
  - 原文：Out-of-band: technique used to retrieve data using a different channel

### 事实 `owasp_wstg_v4_2_sql_injection-b17-3`（grade=3）

- 主位置：`owasp_wstg_v4_2_sql_injection.md`；索引页范围：None–None
  - Document ID：`2875edd4308dfe6d3c746f3d14d08c877916344c990cbacfdec12fcdcd272a25`
  - 原始 Block：`43da13f1-0522-5462-9973-325458b7c9e8`
  - 解析章节：Testing for SQL Injection > Summary
  - 原文：Inferential or Blind: there is no actual transfer of data, but the tester is able to reconstruct the information by sending particular requests and observing the resulting behavior of the DB Server.

- [ ] 人工确认：核准两处 Out-of-band 证据等价，而非增加必须召回的第四个事实。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_022 — context

Why does NIST Rev. 3 emphasize cybersecurity risk management instead of maintaining every detailed response procedure?

参考答案：Detailed procedures vary and change too often for one static publication; the revision focuses on all CSF 2.0 Functions.
依据：Two explicit claims in the scope paragraph must be supported.
来源审查：NIST Scope 明示细节变化太快，转向所有 CSF 2.0 Functions；两条必要事实均在节选第二页。
人工状态：`pending`；审核人：`None`

### 事实 `nist_sp80061r3_pp10-12-b14-1`（grade=3）

- 主位置：`nist_sp80061r3_pp10-12.pdf`；索引页范围：2–2
  - Document ID：`dc95e150e756524e3bc38e81b5be7e2e912135c1633aea9f885667fe521e4830`
  - 原始 Block：`4a0e88f0-2723-5bcc-83f6-e62e853990cc`
  - 解析章节：1. Introduction > 1.1. Purpose and Scope
  - 原文：Because the details of how to perform incident response activities change so often and vary so much across technologies, environments, and organizations, it is no longer feasible to capture and maintain that information in a single static publication.

### 事实 `nist_sp80061r3_pp10-12-b14-2`（grade=3）

- 主位置：`nist_sp80061r3_pp10-12.pdf`；索引页范围：2–2
  - Document ID：`dc95e150e756524e3bc38e81b5be7e2e912135c1633aea9f885667fe521e4830`
  - 原始 Block：`4a0e88f0-2723-5bcc-83f6-e62e853990cc`
  - 解析章节：1. Introduction > 1.1. Purpose and Scope
  - 原文：this version focuses on improving cybersecurity risk management for all of the NIST Cybersecurity Framework (CSF) 2.0 Functions

- [ ] 人工确认：实际标题应为 1.1 Purpose and Scope；当前解析路径受前一处非章节标题影响，需单列 Metadata 缺陷。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_023 — context

For remote PowerShell command execution, which cmdlet is mentioned and what permission prerequisite applies?

参考答案：Invoke-Command; administrator permissions are required to connect to remote systems.
依据：The Markdown parser splits inline code from surrounding text; both pieces are needed.
来源审查：Invoke-Command 与远程管理员权限分别被解析成两个相邻片段；两个事实都已标注。
人工状态：`pending`；审核人：`None`

### 事实 `mitre_attack_v17_1-b5-1`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`a3d32a81-9c33-58d7-bb87-3e48ded23c83`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell
  - 原文：Invoke-Command

### 事实 `mitre_attack_v17_1-b6-2`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`05d2351c-251b-5dc8-9104-11f43821c958`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1059.001: PowerShell
  - 原文：administrator permissions are required to use PowerShell to connect to remote systems

- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_024 — context

What cross-account authentication indicators and matching response actions are listed in the brute-force guide?

参考答案：Same source IP attacking multiple accounts/high-frequency failures; block suspicious IP, enable MFA and investigate accounts.
依据：Spans Detection and Response sections, so one parent is not sufficient.
来源审查：跨账户/高频失败在 Detection，三个措施在 Response，共五个必要事实，跨两个 Parent。
人工状态：`pending`；审核人：`None`

本轮事实检查：两项跨账户相关检测信号与三项处置动作分属 Detection/Response；每项都在问题范围内。它们是参考知识，不证明某次告警真的出现这些信号或已执行这些动作。
所需证据范围：`reference_knowledge`

### 事实 `brute_force-b6-1`（grade=3）

- 主位置：`brute_force.md`；索引页范围：None–None
  - Document ID：`219450061de1a4e313195418629a3092055a4129f1ec565cc80cd72d63aa65aa`
  - 原始 Block：`efffc5d5-51e8-5756-bb79-b4c0dfc8bc6b`
  - 解析章节：Brute Force Attack > Detection
  - 原文：Same source IP attacking multiple accounts

### 事实 `brute_force-b7-2`（grade=3）

- 主位置：`brute_force.md`；索引页范围：None–None
  - Document ID：`219450061de1a4e313195418629a3092055a4129f1ec565cc80cd72d63aa65aa`
  - 原始 Block：`6423c98c-3b78-50dc-9d12-d5d4dad460e9`
  - 解析章节：Brute Force Attack > Detection
  - 原文：High frequency authentication failures

### 事实 `brute_force-b10-3`（grade=3）

- 主位置：`brute_force.md`；索引页范围：None–None
  - Document ID：`219450061de1a4e313195418629a3092055a4129f1ec565cc80cd72d63aa65aa`
  - 原始 Block：`c74f8193-1c4e-505f-8635-a2ee3765eb35`
  - 解析章节：Brute Force Attack > Response
  - 原文：Block suspicious IP

### 事实 `brute_force-b11-4`（grade=3）

- 主位置：`brute_force.md`；索引页范围：None–None
  - Document ID：`219450061de1a4e313195418629a3092055a4129f1ec565cc80cd72d63aa65aa`
  - 原始 Block：`e4c5acd1-6a01-5eb2-b76f-921c176f8483`
  - 解析章节：Brute Force Attack > Response
  - 原文：Enable MFA

### 事实 `brute_force-b12-5`（grade=3）

- 主位置：`brute_force.md`；索引页范围：None–None
  - Document ID：`219450061de1a4e313195418629a3092055a4129f1ec565cc80cd72d63aa65aa`
  - 原始 Block：`fdc90658-40c0-5122-b255-1b934a93812b`
  - 解析章节：Brute Force Attack > Response
  - 原文：Investigate affected accounts

- [ ] 人工确认：确认是否确需完整五项，避免以答案冗余内容制造过严 Recall 分母。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_025 — context

What does the valid-accounts description say about both bypassing access controls and moving across account types?

参考答案：Compromised credentials can bypass controls; overlapping local, domain and cloud permissions can enable privilege escalation.
依据：Two source paragraphs support control bypass and cross-account privilege risks. Bibliographic citation markup is not part of the evidence requirement.
来源审查：两个 ATT&CK 段落分别支持访问控制绕过和跨账户权限提升；去掉引用标记而未删语义条件。
人工状态：`pending`；审核人：`None`

本轮事实检查：绕过访问控制与跨 local/domain/cloud 账户提升权限是两个必要事实；引用 ATT&CK 说明潜在能力，不声称当前事件已使用有效账户或已提权。
所需证据范围：`reference_knowledge`

### 事实 `mitre_attack_v17_1-b34-1`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`9df49cee-b541-5e50-a1db-22159ec3bf17`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts
  - 原文：Compromised credentials may be used to bypass access controls

### 事实 `mitre_attack_v17_1-b36-2`（grade=3）

- 主位置：`mitre_attack_v17_1.md`；索引页范围：None–None
  - Document ID：`fad15d973d25ac6b0a026f3d89e484df60abe3b2f19e47fbdcebbc22fea5f08f`
  - 原始 Block：`b96b8f17-37a3-5d39-b01e-c367ec19ce11`
  - 解析章节：MITRE ATT&CK Enterprise v17.1 — selected technique descriptions > T1078: Valid Accounts
  - 原文：The overlap of permissions for local, domain, and cloud accounts across a network of systems is of concern because the adversary may be able to pivot across accounts and systems to reach a high level of access (i.e., domain or enterprise administrator) to bypass access controls set within the enterprise.

- [ ] 人工确认：这些是参考风险，不表示当前告警已发生凭证滥用或提权。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_026 — unanswerable

What is the exact production API key for the fictional Acme SOC deployment?

参考答案：Insufficient evidence in this corpus.
依据：The frozen corpus contains public guidance and synthetic examples, no private deployment credentials.
来源审查：冻结语料是公开指引与合成样例，没有 Acme 生产密钥或部署记录。
人工状态：`pending`；审核人：`None`

本轮事实检查：无部署配置、密钥清单或 Acme 私有凭据；公开指导及示例字符串不能作为指定生产 API key。
所需证据范围：`deployment_private_data`

- [ ] 人工确认：人工确认整个冻结语料不能回答；不能把示例密码或 SQL 测试字符串当作生产密钥。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_027 — unanswerable

What indicators of compromise are documented for the fictional CVE-2099-99999?

参考答案：Insufficient evidence in this corpus.
依据：This fictional identifier and its indicators do not occur in the frozen corpus.
来源审查：虚构 CVE-2099-99999 及专属 IOC 不在冻结知识库。
人工状态：`pending`；审核人：`None`

本轮事实检查：冻结语料没有 CVE-2099-99999 或对应 IOC；相似漏洞、示例 IP/域名不是该指定漏洞的真实指标。
所需证据范围：`reference_knowledge`

- [ ] 人工确认：确认不可回答标签；相似攻击知识不是该虚构编号的 IOC。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_028 — unanswerable

在 2026-10-31 这次告警中，攻击者实际登录了哪些生产账户？

参考答案：Insufficient evidence in this corpus.
依据：The corpus is reference guidance, not observed event telemetry for a dated production incident.
来源审查：语料不包含 2026-10-31 的生产登录遥测或告警账户事实。
人工状态：`pending`；审核人：`None`

本轮事实检查：未包含 2026-10-31 的认证日志/告警事件记录；ATT&CK 的账户类型和示例不是攻击者实际登录的账户清单。
所需证据范围：`observed_event`

- [ ] 人工确认：该问题要求 observed_event，不能用 reference_knowledge 推断实际登录账户。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_029 — unanswerable

Which vendor firmware command disables the fictional QuantumShield X900 audit engine?

参考答案：Insufficient evidence in this corpus.
依据：No QuantumShield X900 vendor manual or commands are included.
来源审查：没有 QuantumShield X900 厂商手册或固件命令。
人工状态：`pending`；审核人：`None`

本轮事实检查：无 QuantumShield X900 的厂商固件手册或 audit engine 命令；一般安全知识不能推断私有命令。
所需证据范围：`reference_knowledge`

- [ ] 人工确认：确认整个语料没有可支持该专属命令的依据。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

## rag_030 — unanswerable

What exact financial loss did the fictional ACME incident cause on 2026-10-31?

参考答案：Insufficient evidence in this corpus.
依据：No ACME incident records or financial-loss data are in the corpus.
来源审查：没有 ACME 该日期事件的损失记录。
人工状态：`pending`；审核人：`None`

本轮事实检查：无 ACME 于 2026-10-31 的事件或财务记录；NIST 的一般损害描述不能给出该事件确切损失。
所需证据范围：`observed_event`

- [ ] 人工确认：人工确认不可回答；不能从一般损害描述推算具体金额。
- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。

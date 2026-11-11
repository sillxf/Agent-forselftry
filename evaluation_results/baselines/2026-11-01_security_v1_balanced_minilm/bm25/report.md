# bm25 retrieval baseline

Status: **provisional**; 100 labels pending human review.
Dataset: `security-rag-benchmark-v1-100-candidate-r2` / `0d1c86f478883b3b385e01828f5fddc9ac37f6df44e7bcc955fc88bca4ef37e3`.
Code: `231ac392fda30209e914c5771bfb796aadedc5b7`; dirty=True; source SHA-256 `008556a9e3cef0713b2934d18b8fa79847097bc967398ad21d8239dc654565b9`.

Questions: 100; answerable: 90; unanswerable: 10.

| Ranking unit (K=5) | Evidence Recall | Result Precision | MRR | Result NDCG |
| --- | ---: | ---: | ---: | ---: |
| child | 0.5167 | 0.1178 | 0.4306 | 0.4433 |
| parent | 0.5333 | 0.1133 | 0.4519 | 0.4738 |

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
| context | 5 | 1.0000 | 0.7667 | 1.0000 |
| exact_identifier | 5 | 0.8000 | 0.4667 | 0.8000 |
| mixed_terms | 13 | 0.9615 | 0.8269 | 1.0000 |
| multi_document | 5 | 0.4000 | 0.4000 | 0.4000 |
| paraphrase | 8 | 0.5000 | 0.3750 | 0.5000 |
| response | 5 | 0.6000 | 0.6000 | 0.6000 |
| semantic | 5 | 0.8000 | 0.6000 | 0.8000 |
| tables_steps | 5 | 1.0000 | 0.8667 | 1.0000 |
| technique_confusion | 15 | 0.4667 | 0.4333 | 0.5333 |
| unanswerable | 10 | N/A | N/A | N/A |
| zh_to_en | 24 | 0.0000 | 0.0000 | 0.0000 |

## Engineering diagnostics

Errors: 0; no-result rate: 0.1800.
Retrieval latency ms (mean/P50/P95): 2.32 / 2.13 / 4.02.
Latency excludes model/index setup and evidence scoring. The first query is not warmed separately.
Mean parent context length: 7642.9 characters.
This is a size diagnostic, not a validated context-noise/precision metric.
Unanswerable cases are excluded from ranking averages; no refusal rate is inferred.

## Failures

- `rag_002`: first_result_not_relevant — What technique is assigned the ATT&CK identifier T1110?
- `rag_003`: first_result_not_relevant — Which ATT&CK technique name corresponds to T1078?
- `rag_004`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — Which OWASP WSTG test identifier covers SQL injection?
- `rag_005`: first_result_not_relevant — 检测规则 R002 的严重程度和响应动作是什么？
- `rag_006`: first_result_not_relevant — Can the Windows scripting shell fetch an executable and run it without first writing it to disk?
- `rag_007`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — Can password guessing be performed without contacting a live authentication service?
- `rag_009`: first_result_not_relevant — How can a tester infer database information when no data is returned directly?
- `rag_011`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 暴力破解告警的本地响应清单建议采取哪些措施？
- `rag_014`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 本地 SQL 注入知识库列出了哪些预防措施？
- `rag_018`: first_result_not_relevant — What are the three numbered actions in the response checklist, in order?
- `rag_024`: first_result_not_relevant — What cross-account authentication indicators and matching response actions are listed in the brute-force guide?
- `rag_025`: first_result_not_relevant — What does the valid-accounts description say about both bypassing access controls and moving across account types?
- `rag_031`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 为什么取证时没有发现新落地的程序文件，也不能排除系统自带脚本环境曾下载并运行过程序？
- `rag_032`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 用系统自带脚本环境连接另一台机器执行任务时，资料要求连接方具备什么权限？
- `rag_033`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 离职人员的身份被重新使用时，为什么这种活动可能更不容易被本人察觉？
- `rag_034`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 攻击者已经拿到合法登录凭据时，还可能绕过资源上的哪类限制？
- `rag_035`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 大量身份各只收到少数几个常见口令的尝试，这种横着铺开的登录行为属于什么模式？
- `rag_036`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 把同一个候选口令轮流用于许多身份，而不是对单个身份反复更换口令，这样做是在规避什么？
- `rag_037`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 某个站点泄露的成对用户名和口令，为什么会被攻击者带到另一个站点再试一次？
- `rag_038`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 攻击者不认识用户实际输入的密码字符，却拿着窃取的摘要完成认证，这属于哪种做法？
- `rag_039`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 用户已经在主机上登录后，系统哪个安全进程的内存会保存可被窃取的凭据材料？
- `rag_040`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 攻击者把程序挂到用户登录时自动执行的位置，这个触发时机是什么？
- `rag_041`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 借助用户登录自启动位置运行的程序，通常继承谁的身份上下文和权限？
- `rag_042`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 管理员希望把重复工作保存为可按顺序运行、还能写条件和循环的命令清单，哪种文件机制能做到？
- `rag_043`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 办公文档为什么能像小程序一样，在事件触发时自动执行主机任务？
- `rag_044`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 一种常被当成网页专用的脚本语言，能否在没有浏览器页面的运行环境里执行？
- `rag_045`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 不打开浏览器窗口也能运行网页应用格式的独立程序，资料指的是哪个系统工具？
- `rag_046`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 攻击者借用合法账号连接远程管理机制后，会以哪个登录身份执行后续操作？
- `rag_047`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 远程管理机制除了启动程序，还允许对目标系统的哪两类配置进行修改？
- `rag_048`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 不是向用户登录目录放文件，而是借助系统服务管理接口来启动载荷，这对应什么执行机制？
- `rag_049`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 数据库结果不直接出现在页面中时，测试者可以通过什么观察方式重建信息？
- `rag_050`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 查询结果不沿着提交输入的页面返回，而是另走一条通信通道，这属于哪种取数方式？
- `rag_051`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 梳理可能进入数据库查询的入口时，只查看可见输入框够不够，还应考虑哪些隐藏或附带的请求内容？
- `rag_052`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 恢复工作尚未结束时，已经发现的改进经验应当什么时候分享，而不是等待什么节点？
- `rag_053`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 为什么一本固定出版物不再适合维护所有事件处置的操作细节？
- `rag_054`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 恶意软件事件处理完后，已受影响的认证材料和用于恢复的数据副本分别该如何处理？
- `rag_056`: first_result_not_relevant — VBA macro 为什么能让 Office 文档自动执行宿主机上的任务？
- `rag_059`: first_result_not_relevant — WinRM 不只是 PowerShell 命令名，它在系统里同时代表哪两种东西？
- `rag_063`: first_result_not_relevant — Pass-the-Hash 能否在不知道 cleartext password 的情况下冒用身份认证？
- `rag_066`: partial_evidence — Base64 或 URL encoding 在 Command Obfuscation 中起什么作用？
- `rag_067`: first_result_not_relevant — LSASS memory dump 可以只在目标主机当场分析吗，还是能够离线转移分析？
- `rag_068`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 有没有办法让一个程序在用户开始新的桌面会话时自己再次运行，而不需要用户亲手启动它？
- `rag_069`: first_result_not_relevant — How can a stolen secret stand in for the characters its owner originally typed when a service authenticates that owner?
- `rag_070`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 为什么攻击者会把一份很短的猜测清单分散用于许多身份，而不把所有尝试押在同一个身份上？
- `rag_072`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 办公文件原本只是内容载体，哪种内置能力能让它在特定事件发生时自动执行主机任务？
- `rag_073`: first_result_not_relevant — Why is a login using an existing identity not enough to conclude that access controls kept an intruder out?
- `rag_074`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 不去猜用户的口令，而是寻找已经登录的会话留下的秘密，应查看哪里，又需要哪类身份才能提取？
- `rag_077`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 攻击者已经拿到外站泄露的成对账号密码，再利用用户复用习惯登录目标；这与轮试常见口令的模式如何区分？
- `rag_079`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 分析目标是获取已登录会话留下的内存凭据，而不是使用现成摘要去认证；应该聚焦哪个安全进程？
- `rag_081`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 线索明确是由系统脚本引擎解释的微软脚本实现，而非办公文档宏；应找哪个实现？
- `rag_083`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 需要远程修改注册表和服务，线索指向一种同名的系统服务与协议，而非仅仅本地命令解释器；它是什么？
- `rag_084`: first_result_not_relevant — What persistence location executes a referenced program at user logon with that user permissions rather than via a temporary remote service?
- `rag_085`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 载荷通过服务管理器的临时服务运行，不是等用户下次登录；资料中对应什么执行方式？
- `rag_087`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 现象是把原来可识别的命令改写成难以签名的编码或字符串形式，而不是换一个脚本宿主；这描述哪种目的？
- `rag_088`: no_relevant_child, first_result_not_relevant — Which retrieval method reconstructs information from database behaviour without receiving it through another channel?
- `rag_089`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 目标将查询结果交给另一条通信链路，而不是直接显示在提交输入的原页面；应归为哪一类？
- `rag_097`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 请分别说明用户登录自启动程序的触发时机，以及远程管理机制可修改的两类系统配置，不要把两种机制混为一谈。
- `rag_098`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 针对恶意软件事件，网络、认证材料和恢复副本应分别如何处理；已经发现的经验教训是否要等恢复结束才分享？
- `rag_100`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 先说明少量常见口令遍历许多身份的行为模式，再列出本地暴力破解清单的三项建议；不要声称每项措施与某个指标一一对应。

## Scope and limitations

All source evidence and quotes were checked against the actual index before evaluation.
Pending labels are AI-prepared candidates, not human-certified ground truth. Review alternative
valid sources, grades and unanswerable rationales before treating these scores as acceptance results.
This small development set is not a holdout benchmark and does not establish general accuracy.
No LLM answer generation, judge, reranker, embedding migration or automatic tuning was performed.
Read `retrieval_results.jsonl` and `failures.json` for full ranks, scores, quotes and provenance.

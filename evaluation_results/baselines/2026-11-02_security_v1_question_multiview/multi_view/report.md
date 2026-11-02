# multi_view retrieval baseline

Status: **provisional**; 100 labels pending human review.
Dataset: `security-rag-benchmark-v1-100-candidate-r2` / `0d1c86f478883b3b385e01828f5fddc9ac37f6df44e7bcc955fc88bca4ef37e3`.
Code: `ff725c0a54ff9ebd96db469c8b5a63d5f083e995`; dirty=True; source SHA-256 `8c7b2eee2c2f12c407756c84c07b9a1473415c1fdaaf860e373e8860ccc309d2`.

Questions: 100; answerable: 90; unanswerable: 10.

| Ranking unit (K=5) | Evidence Recall | Result Precision | MRR | Result NDCG |
| --- | ---: | ---: | ---: | ---: |
| child | 0.8111 | 0.1889 | 0.6448 | 0.6800 |
| parent | 0.8444 | 0.1822 | 0.6807 | 0.7231 |

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
| exact_identifier | 5 | 0.8000 | 0.6667 | 0.8000 |
| mixed_terms | 13 | 1.0000 | 0.9615 | 1.0000 |
| multi_document | 5 | 1.0000 | 0.7000 | 1.0000 |
| paraphrase | 8 | 0.7500 | 0.5417 | 0.7500 |
| response | 5 | 0.8000 | 0.6667 | 0.8000 |
| semantic | 5 | 0.6000 | 0.5000 | 0.6000 |
| tables_steps | 5 | 1.0000 | 1.0000 | 1.0000 |
| technique_confusion | 15 | 0.7333 | 0.6333 | 0.9333 |
| unanswerable | 10 | N/A | N/A | N/A |
| zh_to_en | 24 | 0.7083 | 0.3764 | 0.7083 |

## Engineering diagnostics

Errors: 0; no-result rate: 0.0000.
Retrieval latency ms (mean/P50/P95): 155.59 / 154.99 / 184.19.
Latency excludes model/index setup and evidence scoring. The first query is not warmed separately.
Mean parent context length: 13115.4 characters.
This is a size diagnostic, not a validated context-noise/precision metric.
Unanswerable cases are excluded from ranking averages; no refusal rate is inferred.

## Failures

- `rag_001`: first_result_not_relevant — T1059.001 refers to which Windows scripting environment?
- `rag_004`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — Which OWASP WSTG test identifier covers SQL injection?
- `rag_006`: first_result_not_relevant — Can the Windows scripting shell fetch an executable and run it without first writing it to disk?
- `rag_007`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — Can password guessing be performed without contacting a live authentication service?
- `rag_009`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — How can a tester infer database information when no data is returned directly?
- `rag_011`: first_result_not_relevant — 暴力破解告警的本地响应清单建议采取哪些措施？
- `rag_014`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 本地 SQL 注入知识库列出了哪些预防措施？
- `rag_031`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 为什么取证时没有发现新落地的程序文件，也不能排除系统自带脚本环境曾下载并运行过程序？
- `rag_032`: first_result_not_relevant — 用系统自带脚本环境连接另一台机器执行任务时，资料要求连接方具备什么权限？
- `rag_033`: first_result_not_relevant — 离职人员的身份被重新使用时，为什么这种活动可能更不容易被本人察觉？
- `rag_034`: first_result_not_relevant — 攻击者已经拿到合法登录凭据时，还可能绕过资源上的哪类限制？
- `rag_035`: first_result_not_relevant — 大量身份各只收到少数几个常见口令的尝试，这种横着铺开的登录行为属于什么模式？
- `rag_038`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 攻击者不认识用户实际输入的密码字符，却拿着窃取的摘要完成认证，这属于哪种做法？
- `rag_039`: first_result_not_relevant — 用户已经在主机上登录后，系统哪个安全进程的内存会保存可被窃取的凭据材料？
- `rag_040`: first_result_not_relevant — 攻击者把程序挂到用户登录时自动执行的位置，这个触发时机是什么？
- `rag_041`: first_result_not_relevant — 借助用户登录自启动位置运行的程序，通常继承谁的身份上下文和权限？
- `rag_042`: first_result_not_relevant — 管理员希望把重复工作保存为可按顺序运行、还能写条件和循环的命令清单，哪种文件机制能做到？
- `rag_043`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 办公文档为什么能像小程序一样，在事件触发时自动执行主机任务？
- `rag_044`: first_result_not_relevant — 一种常被当成网页专用的脚本语言，能否在没有浏览器页面的运行环境里执行？
- `rag_045`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 不打开浏览器窗口也能运行网页应用格式的独立程序，资料指的是哪个系统工具？
- `rag_046`: first_result_not_relevant — 攻击者借用合法账号连接远程管理机制后，会以哪个登录身份执行后续操作？
- `rag_047`: first_result_not_relevant — 远程管理机制除了启动程序，还允许对目标系统的哪两类配置进行修改？
- `rag_048`: first_result_not_relevant — 不是向用户登录目录放文件，而是借助系统服务管理接口来启动载荷，这对应什么执行机制？
- `rag_049`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 数据库结果不直接出现在页面中时，测试者可以通过什么观察方式重建信息？
- `rag_050`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 查询结果不沿着提交输入的页面返回，而是另走一条通信通道，这属于哪种取数方式？
- `rag_051`: first_result_not_relevant — 梳理可能进入数据库查询的入口时，只查看可见输入框够不够，还应考虑哪些隐藏或附带的请求内容？
- `rag_053`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 为什么一本固定出版物不再适合维护所有事件处置的操作细节？
- `rag_054`: first_result_not_relevant — 恶意软件事件处理完后，已受影响的认证材料和用于恢复的数据副本分别该如何处理？
- `rag_059`: first_result_not_relevant — WinRM 不只是 PowerShell 命令名，它在系统里同时代表哪两种东西？
- `rag_069`: first_result_not_relevant — How can a stolen secret stand in for the characters its owner originally typed when a service authenticates that owner?
- `rag_070`: first_result_not_relevant — 为什么攻击者会把一份很短的猜测清单分散用于许多身份，而不把所有尝试押在同一个身份上？
- `rag_072`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 办公文件原本只是内容载体，哪种内置能力能让它在特定事件发生时自动执行主机任务？
- `rag_073`: first_result_not_relevant — Why is a login using an existing identity not enough to conclude that access controls kept an intruder out?
- `rag_074`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 不去猜用户的口令，而是寻找已经登录的会话留下的秘密，应查看哪里，又需要哪类身份才能提取？
- `rag_079`: no_relevant_child, first_result_not_relevant — 分析目标是获取已登录会话留下的内存凭据，而不是使用现成摘要去认证；应该聚焦哪个安全进程？
- `rag_081`: no_relevant_child, first_result_not_relevant, incomplete_parent_context — 线索明确是由系统脚本引擎解释的微软脚本实现，而非办公文档宏；应找哪个实现？
- `rag_083`: first_result_not_relevant — 需要远程修改注册表和服务，线索指向一种同名的系统服务与协议，而非仅仅本地命令解释器；它是什么？
- `rag_086`: first_result_not_relevant — Which system scripting environment can download and execute programs in memory without touching disk, unlike batch-file or logon-entry mechanisms?
- `rag_087`: first_result_not_relevant — 现象是把原来可识别的命令改写成难以签名的编码或字符串形式，而不是换一个脚本宿主；这描述哪种目的？
- `rag_088`: no_relevant_child, first_result_not_relevant — Which retrieval method reconstructs information from database behaviour without receiving it through another channel?
- `rag_089`: no_relevant_child, first_result_not_relevant — 目标将查询结果交给另一条通信链路，而不是直接显示在提交输入的原页面；应归为哪一类？
- `rag_097`: first_result_not_relevant — 请分别说明用户登录自启动程序的触发时机，以及远程管理机制可修改的两类系统配置，不要把两种机制混为一谈。
- `rag_098`: first_result_not_relevant — 针对恶意软件事件，网络、认证材料和恢复副本应分别如何处理；已经发现的经验教训是否要等恢复结束才分享？
- `rag_100`: first_result_not_relevant — 先说明少量常见口令遍历许多身份的行为模式，再列出本地暴力破解清单的三项建议；不要声称每项措施与某个指标一一对应。

## Scope and limitations

All source evidence and quotes were checked against the actual index before evaluation.
Pending labels are AI-prepared candidates, not human-certified ground truth. Review alternative
valid sources, grades and unanswerable rationales before treating these scores as acceptance results.
This small development set is not a holdout benchmark and does not establish general accuracy.
No LLM answer generation, judge, reranker, production embedding migration or automatic tuning was performed.
Read `retrieval_results.jsonl` and `failures.json` for full ranks, scores, quotes and provenance.

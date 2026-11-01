# Per-question retrieval failures / unknown cases

Observed ranks are distinguished from unproven semantic-cause hypotheses.

## rag_004 — bm25

Which OWASP WSTG test identifier covers SQL injection?

Reference: WSTG-INPV-05.
Answerable: True; type=english; language=en->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b1-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `78f2651b-4f31-5652-9aec-d673b43a6fc1` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `3a293e8f-167b-5fc6-a719-bf0289f0f43c` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `62b73a03-ebc8-5438-afbb-eb7074f8084f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `a7c9578a-5ca7-5361-85e1-913cf7e59b7a` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `41f65c20-f291-56ad-b718-27ef214ac113` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `ea97e298-d534-5488-8103-036850028884` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `6953c28a-04dd-5a0d-a720-7a884e85255e` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `75998bd9-0957-5c68-9b36-71f765b494a9` | none |
| 9 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `0c4540cf-878d-5a57-a41a-a0fc9a97b554` | none |
### parent
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b1-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `fc70da0c-00d2-524b-95ce-7a88039f1f71` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 7 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b2e6391b-7beb-5336-a631-dcad4a7ba57f` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |

## rag_007 — bm25

Can password guessing be performed without contacting a live authentication service?

Reference: Yes; brute forcing can run offline against acquired credential data such as password hashes.
Answerable: True; type=paraphrase; language=en->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b21-1"], "recovered_below_cutoff": ["mitre_attack_v17_1-b21-1"], "first_relevant_rank": 7, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | none |
| 2 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 3 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `6eb1b7dc-4350-5e66-86fa-61a6a5baaf6f` | none |
| 5 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `169a848c-8109-55ab-9ffb-e2b303a46899` | none |
| 7 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | mitre_attack_v17_1-b21-1 |
| 8 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `f6ec1d6a-bc5a-5223-8988-b40d4f6e5a7c` | none |
| 10 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b21-1"], "recovered_below_cutoff": ["mitre_attack_v17_1-b21-1"], "first_relevant_rank": 7, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 2 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 3 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `dbe666f3-2a88-5dc9-b28f-39d25050a22c` | none |
| 5 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 7 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | mitre_attack_v17_1-b21-1 |
| 8 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 10 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |

## rag_011 — bm25

暴力破解告警的本地响应清单建议采取哪些措施？

Reference: 封禁可疑 IP、启用 MFA、调查受影响账户。
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["brute_force-b10-1", "brute_force-b11-2", "brute_force-b12-3"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["brute_force-b10-1", "brute_force-b11-2", "brute_force-b12-3"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_014 — bm25

本地 SQL 注入知识库列出了哪些预防措施？

Reference: 预编译语句、输入验证、最小权限。
Answerable: True; type=mixed_terms; language=mixed->en

### child
{"missing_evidence_ids": ["sql_injection-b10-2", "sql_injection-b11-3", "sql_injection-b9-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `f62ed3d7-e9e3-52c1-90a2-e41f8c35889e` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `102c3190-7f50-54c4-81aa-0a0069894ce9` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `6e0482b4-13b4-5b13-9136-64effb3e3449` | none |
| 5 | sql_injection.md | `240fe162-b73e-543d-bf96-874fc7c27445` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `38d57954-5fca-5212-a189-347ec8ebece9` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `11cb9483-6950-596f-a053-76190a52e8bf` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `cbbe9cd9-1f02-5f6d-a060-fc6493cf7703` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4cf15dd2-e244-5170-a826-08e497454a71` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `5cb47030-8296-5fe2-9c15-c853b4d2853d` | none |
### parent
{"missing_evidence_ids": ["sql_injection-b10-2", "sql_injection-b11-3", "sql_injection-b9-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `8f58fdb9-5926-566a-924d-e94cf16cf2ca` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 4 | sql_injection.md | `24d007a3-9ab6-5463-882c-40bf0052e8d7` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `d31d1d37-1832-547f-8426-6700a98884b3` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `e11d7d74-a95a-56c1-94d6-942ac597fca6` | none |
| 7 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `fac8f961-fa7c-54de-afa1-3b07108faf9e` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `e1fbe1fe-fbc1-5b52-9433-76c68fbd4284` | none |

## rag_026 — bm25

What is the exact production API key for the fictional Acme SOC deployment?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `a7c9578a-5ca7-5361-85e1-913cf7e59b7a` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `f26f162c-7084-5cbf-adff-3870315cb474` | none |
| 4 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 5 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `4f1ddf29-046a-5279-b643-36ab6a0e0533` | none |
| 7 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `9e442b7d-ac16-5d43-8fe3-a3bfb4317505` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `a00dba3e-b156-5c3f-983a-a3fb893eaa08` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `e83fa852-9253-5425-90f9-8ba526d825bc` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `fc70da0c-00d2-524b-95ce-7a88039f1f71` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 4 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 5 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b2e6391b-7beb-5336-a631-dcad4a7ba57f` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |

## rag_027 — bm25

What indicators of compromise are documented for the fictional CVE-2099-99999?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 2 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 4 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 5 | sql_injection.md | `d886d741-718a-5eca-92c8-bd314df926b0` | none |
| 6 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `75998bd9-0957-5c68-9b36-71f765b494a9` | none |
| 8 | malware.md | `0569ed09-a27c-54a6-8ea4-de7a6b02b210` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `aea7a0af-f445-5d68-92d1-0e53890d9d88` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `4f1ddf29-046a-5279-b643-36ab6a0e0533` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 2 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 4 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 5 | sql_injection.md | `a97cfdc3-337d-5574-9961-eb070faad246` | none |
| 6 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 8 | malware.md | `5e5e5068-0339-589e-9259-c6176968a43e` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |

## rag_028 — bm25

在 2026-10-31 这次告警中，攻击者实际登录了哪些生产账户？

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_029 — bm25

Which vendor firmware command disables the fictional QuantumShield X900 audit engine?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `156a04b4-abca-5cf1-ac0e-a9e52ba07851` | none |
| 2 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 3 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 4 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `2a440bb1-f6c9-5215-94e3-8abf48bcb089` | none |
| 6 | attack_t1027_010.md | `3ff9fe68-110a-5623-b45d-5b6ddeb2ac79` | none |
| 7 | attack_t1027_010.md | `1a6dfdb7-1745-59ed-a476-c68e6e7e5283` | none |
| 8 | attack_t1027_010.md | `74e3d909-8b7d-5517-a2cf-a4491db86d5b` | none |
| 9 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 10 | attack_t1027_010.md | `b76c5fc1-dc47-521d-b75c-a45527b3546c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `04903bb6-9c4f-597e-afa2-b3756415cb82` | none |
| 2 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 3 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 4 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 9 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `fc70da0c-00d2-524b-95ce-7a88039f1f71` | none |

## rag_030 — bm25

What exact financial loss did the fictional ACME incident cause on 2026-10-31?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `f8412402-0e29-56c2-8a82-7486b286897c` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `5d3f3c2b-f7aa-50e0-a23d-7eac886f576e` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `51188538-dd65-5146-bbd3-16f43a125923` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `5346b998-ec8f-5fc3-a273-44d80e07adbb` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `0054058a-7844-5b98-9ada-06310a90907e` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `323f29d6-5027-5df8-92c9-64da1831f634` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 9 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 10 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |

## rag_031 — bm25

为什么取证时没有发现新落地的程序文件，也不能排除系统自带脚本环境曾下载并运行过程序？

Reference: PowerShell can download executables and run them in memory without touching disk.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b7-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b7-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_032 — bm25

用系统自带脚本环境连接另一台机器执行任务时，资料要求连接方具备什么权限？

Reference: Administrator permissions are required for PowerShell connections to remote systems.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b6-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b6-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_033 — bm25

离职人员的身份被重新使用时，为什么这种活动可能更不容易被本人察觉？

Reference: The original account user is absent and cannot notice anomalous activity.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b35-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b35-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_034 — bm25

攻击者已经拿到合法登录凭据时，还可能绕过资源上的哪类限制？

Reference: Compromised credentials may bypass access controls.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b34-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b34-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_035 — bm25

大量身份各只收到少数几个常见口令的尝试，这种横着铺开的登录行为属于什么模式？

Reference: Password spraying uses one or a small list of common passwords against many accounts.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-spray-pattern"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-spray-pattern"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_036 — bm25

把同一个候选口令轮流用于许多身份，而不是对单个身份反复更换口令，这样做是在规避什么？

Reference: Account lockouts caused by many guesses against one account.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-spray-lockout"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-spray-lockout"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_037 — bm25

某个站点泄露的成对用户名和口令，为什么会被攻击者带到另一个站点再试一次？

Reference: Credential stuffing exploits overlap and users reusing passwords across personal and business accounts.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-stuffing-cause", "security-v1-stuffing-reuse"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-stuffing-cause", "security-v1-stuffing-reuse"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_038 — bm25

攻击者不认识用户实际输入的密码字符，却拿着窃取的摘要完成认证，这属于哪种做法？

Reference: Pass the Hash authenticates as a user without the cleartext password.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-pth-auth"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-pth-auth"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_039 — bm25

用户已经在主机上登录后，系统哪个安全进程的内存会保存可被窃取的凭据材料？

Reference: LSASS process memory stores credential materials after logon.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_040 — bm25

攻击者把程序挂到用户登录时自动执行的位置，这个触发时机是什么？

Reference: It executes when a user logs in.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-run-logon"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-run-logon"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_041 — bm25

借助用户登录自启动位置运行的程序，通常继承谁的身份上下文和权限？

Reference: The user context and associated account permissions.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-run-context"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-run-context"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_042 — bm25

管理员希望把重复工作保存为可按顺序运行、还能写条件和循环的命令清单，哪种文件机制能做到？

Reference: Windows command-shell batch files such as .bat or .cmd.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-batch"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-batch"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_043 — bm25

办公文档为什么能像小程序一样，在事件触发时自动执行主机任务？

Reference: VBA is event-driven and lets Office documents contain task-automation macros.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_044 — bm25

一种常被当成网页专用的脚本语言，能否在没有浏览器页面的运行环境里执行？

Reference: Yes; JavaScript can execute in runtime environments outside the browser.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-js-runtime"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-js-runtime"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_045 — bm25

不打开浏览器窗口也能运行网页应用格式的独立程序，资料指的是哪个系统工具？

Reference: Mshta.exe executes HTA files; HTAs run outside the browser.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-mshta-files", "security-v1-mshta-outside"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-mshta-files", "security-v1-mshta-outside"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_046 — bm25

攻击者借用合法账号连接远程管理机制后，会以哪个登录身份执行后续操作？

Reference: WinRM interactions can perform actions as the logged-on user.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-winrm-user"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-winrm-user"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_047 — bm25

远程管理机制除了启动程序，还允许对目标系统的哪两类配置进行修改？

Reference: WinRM can modify the Registry and services.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_048 — bm25

不是向用户登录目录放文件，而是借助系统服务管理接口来启动载荷，这对应什么执行机制？

Reference: Service Execution abuses the Windows service control manager.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-service-manager"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-service-manager"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_049 — bm25

数据库结果不直接出现在页面中时，测试者可以通过什么观察方式重建信息？

Reference: Inferential/blind injection sends requests and observes database behaviour.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_050 — bm25

查询结果不沿着提交输入的页面返回，而是另走一条通信通道，这属于哪种取数方式？

Reference: Out-of-band SQL injection retrieves data through a different channel.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b16-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b16-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_051 — bm25

梳理可能进入数据库查询的入口时，只查看可见输入框够不够，还应考虑哪些隐藏或附带的请求内容？

Reference: Include hidden POST fields, HTTP headers and cookies, and test input fields separately.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b34-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b34-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_052 — bm25

恢复工作尚未结束时，已经发现的改进经验应当什么时候分享，而不是等待什么节点？

Reference: Share lessons as soon as identified; do not delay until recovery concludes.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["nist_sp80061r3_pp10-12-b38-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["nist_sp80061r3_pp10-12-b38-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_053 — bm25

为什么一本固定出版物不再适合维护所有事件处置的操作细节？

Reference: Response details change often and vary across technologies, environments and organizations.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["nist_sp80061r3_pp10-12-b14-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["nist_sp80061r3_pp10-12-b14-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_054 — bm25

恶意软件事件处理完后，已受影响的认证材料和用于恢复的数据副本分别该如何处理？

Reference: Reset compromised credentials and restore from clean backups.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["malware-b17-1", "malware-b18-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["malware-b17-1", "malware-b18-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_066 — bm25

Base64 或 URL encoding 在 Command Obfuscation 中起什么作用？

Reference: They are built-in forms of obfuscation that make command strings and patterns harder to signature and analyze.
Answerable: True; type=mixed_terms; language=mixed->en

### child
{"missing_evidence_ids": ["security-v1-obfuscation-purpose"], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | security-v1-obfuscation-encoding |
| 2 | owasp_wstg_v4_2_sql_injection.md | `bf089b6c-ca1d-5fe1-a14d-11ea491056c1` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2214dfb2-d620-5744-9fa7-8e36c4669138` | none |
| 4 | attack_t1027_010.md | `3ff9fe68-110a-5623-b45d-5b6ddeb2ac79` | none |
| 5 | attack_t1027_010.md | `1a6dfdb7-1745-59ed-a476-c68e6e7e5283` | none |
| 6 | attack_t1027_010.md | `74e3d909-8b7d-5517-a2cf-a4491db86d5b` | none |
| 7 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 8 | attack_t1027_010.md | `b76c5fc1-dc47-521d-b75c-a45527b3546c` | none |
| 9 | attack_t1027_010.md | `7242f3d0-ddae-53c5-925d-aac6db694099` | none |
| 10 | attack_t1027_010.md | `de54c4ed-5ba6-55a0-9123-6ae0f1f3012b` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | security-v1-obfuscation-purpose, security-v1-obfuscation-encoding |
| 2 | owasp_wstg_v4_2_sql_injection.md | `4924a677-7a32-5c43-9fe3-8d16cd327837` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 4 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 8 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 9 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |

## rag_068 — bm25

有没有办法让一个程序在用户开始新的桌面会话时自己再次运行，而不需要用户亲手启动它？

Reference: A Registry run key or startup-folder entry launches the referenced program when the user logs in.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-run-logon"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-run-logon"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_070 — bm25

为什么攻击者会把一份很短的猜测清单分散用于许多身份，而不把所有尝试押在同一个身份上？

Reference: To avoid account lockouts associated with many password guesses against a single account.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-spray-lockout"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-spray-lockout"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_072 — bm25

办公文件原本只是内容载体，哪种内置能力能让它在特定事件发生时自动执行主机任务？

Reference: VBA macros in Office documents can automate host tasks.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_074 — bm25

不去猜用户的口令，而是寻找已经登录的会话留下的秘密，应查看哪里，又需要哪类身份才能提取？

Reference: Credential materials are stored in LSASS process memory and can be harvested by an administrative user or SYSTEM.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-lsass-memory", "security-v1-lsass-rights"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-lsass-memory", "security-v1-lsass-rights"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_076 — bm25

What account attack tries the same few common passwords across identities to avoid per-account lockout?

Reference: Password spraying.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | security-v1-spray-pattern, security-v1-spray-lockout |
| 2 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 3 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 4 | brute_force.md | `0caddcca-4cdf-5ae3-97d7-c39c4d5cd460` | none |
| 5 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 6 | brute_force.md | `df7d8241-91d9-5105-802e-6f633e677246` | none |
| 7 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 8 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `70e41073-8104-5d67-b28d-7840c9d3f4b7` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | security-v1-spray-pattern, security-v1-spray-lockout |
| 2 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 3 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 4 | brute_force.md | `cb2c87f1-0241-5ad4-a053-5168b2cf5eef` | none |
| 5 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 6 | brute_force.md | `63630879-978b-548c-a918-111b10587b3c` | none |
| 7 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 8 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |

## rag_077 — bm25

攻击者已经拿到外站泄露的成对账号密码，再利用用户复用习惯登录目标；这与轮试常见口令的模式如何区分？

Reference: Credential stuffing uses breach-dump credentials and password overlap.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-stuffing-cause", "security-v1-stuffing-reuse"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-stuffing-cause", "security-v1-stuffing-reuse"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_079 — bm25

分析目标是获取已登录会话留下的内存凭据，而不是使用现成摘要去认证；应该聚焦哪个安全进程？

Reference: LSASS process memory.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_080 — bm25

Which language mechanism best fits event-driven macros embedded in Office documents rather than webpage scripts?

Reference: Visual Basic for Applications (VBA) macros.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | security-v1-vba-event, security-v1-vba-macros |
| 2 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 3 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `79b22ac0-511d-50b0-b7f3-f1a9ec082edb` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `3a293e8f-167b-5fc6-a719-bf0289f0f43c` | none |
| 6 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `75998bd9-0957-5c68-9b36-71f765b494a9` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `62b73a03-ebc8-5438-afbb-eb7074f8084f` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `41f65c20-f291-56ad-b718-27ef214ac113` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `6953c28a-04dd-5a0d-a720-7a884e85255e` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | security-v1-vba-event, security-v1-vba-macros |
| 2 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 3 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `fc70da0c-00d2-524b-95ce-7a88039f1f71` | none |

## rag_081 — bm25

线索明确是由系统脚本引擎解释的微软脚本实现，而非办公文档宏；应找哪个实现？

Reference: JScript.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-js-engine"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-js-engine"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_082 — bm25

Which mechanism uses batch files with sequential commands and loops rather than PowerShell cmdlets?

Reference: Windows command-shell batch files (.bat or .cmd).
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | security-v1-batch |
| 2 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `75998bd9-0957-5c68-9b36-71f765b494a9` | none |
| 4 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `8f2bcaec-cf6c-563e-85ed-da0808c770a5` | none |
| 6 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 7 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 8 | malware.md | `e09b2a00-f3d5-5eb6-bc06-82b042f21798` | none |
| 9 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `5d3f3c2b-f7aa-50e0-a23d-7eac886f576e` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | security-v1-batch |
| 2 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 4 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 5 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 6 | malware.md | `dba1b75f-5cf7-51a7-9393-5daee9064a55` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |

## rag_083 — bm25

需要远程修改注册表和服务，线索指向一种同名的系统服务与协议，而非仅仅本地命令解释器；它是什么？

Reference: Windows Remote Management (WinRM).
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_084 — bm25

What persistence location executes a referenced program at user logon with that user permissions rather than via a temporary remote service?

Reference: Registry run keys or startup folders.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | none |
| 2 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | security-v1-run-logon, security-v1-run-context |
| 3 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `d4ea4f63-f82a-5bc1-b774-0281046fbaa1` | none |
| 5 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `9f1e9c27-159a-5573-942a-eac57ba52004` | none |
| 7 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f6ec1d6a-bc5a-5223-8988-b40d4f6e5a7c` | none |
| 9 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `169a848c-8109-55ab-9ffb-e2b303a46899` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 2 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | security-v1-run-logon, security-v1-run-context |
| 3 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 5 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 7 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 8 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |

## rag_085 — bm25

载荷通过服务管理器的临时服务运行，不是等用户下次登录；资料中对应什么执行方式？

Reference: Service Execution; PsExec can create a temporary service through the SCM API.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-service-psexec"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["security-v1-service-psexec"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_087 — bm25

现象是把原来可识别的命令改写成难以签名的编码或字符串形式，而不是换一个脚本宿主；这描述哪种目的？

Reference: Command obfuscation impedes signature matching and analysis.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-obfuscation-purpose"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-obfuscation-purpose"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_088 — bm25

Which retrieval method reconstructs information from database behaviour without receiving it through another channel?

Reference: Inferential/blind SQL injection.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `0c4540cf-878d-5a57-a41a-a0fc9a97b554` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ea97e298-d534-5488-8103-036850028884` | none |
| 3 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `8f2bcaec-cf6c-563e-85ed-da0808c770a5` | none |
| 5 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `4a868b13-59ee-51d9-8ec2-8f9151d99c8c` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `4f1ddf29-046a-5279-b643-36ab6a0e0533` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `fa9dcae4-7c36-57dd-97b6-f2561547a545` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `d4ea4f63-f82a-5bc1-b774-0281046fbaa1` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ca37ccd3-2bb8-531d-a521-0094c231c702` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | owasp_wstg_v4_2_sql_injection-b17-1 |
| 2 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 3 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `1f917f30-46dd-5722-ba7f-5fead4783010` | none |
| 7 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |

## rag_089 — bm25

目标将查询结果交给另一条通信链路，而不是直接显示在提交输入的原页面；应归为哪一类？

Reference: Out-of-band.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b16-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b16-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_090 — bm25

Which trusted Windows utility executes standalone HTA files rather than Office document macros?

Reference: Mshta.exe.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2, 4, 5], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | security-v1-mshta-files, security-v1-mshta-outside |
| 2 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
| 3 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 4 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 5 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 6 | attack_t1021_006.md | `1f7eb169-9a12-5e59-b795-4ac0ce757da0` | none |
| 7 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `75998bd9-0957-5c68-9b36-71f765b494a9` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 10 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2, 4], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | security-v1-mshta-files, security-v1-mshta-outside |
| 2 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 3 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 4 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 5 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 8 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | malware.md | `dba1b75f-5cf7-51a7-9393-5daee9064a55` | none |

## rag_091 — bm25

我们租户当前到底连续失败几次才会锁定账号，锁定持续多少分钟？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_092 — bm25

这次内存采集实际提取到了哪些域用户的密码摘要？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_093 — bm25

终端 SEC-WS-17 上的登录自启动条目是谁在什么时间写入的？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_094 — bm25

昨晚触发编码脚本告警的外部来源地址具体是多少？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |

## rag_095 — bm25

本次主机隔离是否已经由值班人员实际执行成功？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_097 — bm25

请分别说明用户登录自启动程序的触发时机，以及远程管理机制可修改的两类系统配置，不要把两种机制混为一谈。

Reference: Run-key/startup programs execute at user logon; WinRM can modify the Registry and services.
Answerable: True; type=multi_document; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-run-logon", "security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["security-v1-run-logon", "security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_098 — bm25

针对恶意软件事件，网络、认证材料和恢复副本应分别如何处理；已经发现的经验教训是否要等恢复结束才分享？

Reference: Isolate affected systems from the network, reset compromised credentials and restore clean backups; share identified lessons promptly rather than wait for recovery completion.
Answerable: True; type=multi_document; language=zh->en

### child
{"missing_evidence_ids": ["malware-b14-1", "malware-b17-1", "malware-b18-2", "nist_sp80061r3_pp10-12-b38-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
### parent
{"missing_evidence_ids": ["malware-b14-1", "malware-b17-1", "malware-b18-2", "nist_sp80061r3_pp10-12-b38-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |

## rag_100 — bm25

先说明少量常见口令遍历许多身份的行为模式，再列出本地暴力破解清单的三项建议；不要声称每项措施与某个指标一一对应。

Reference: Password spraying uses a small password set against many accounts; the local guide recommends blocking suspicious IPs, enabling MFA and investigating affected accounts.
Answerable: True; type=multi_document; language=zh->en

### child
{"missing_evidence_ids": ["brute_force-b10-1", "brute_force-b11-2", "brute_force-b12-3", "security-v1-spray-pattern"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
### parent
{"missing_evidence_ids": ["brute_force-b10-1", "brute_force-b11-2", "brute_force-b12-3", "security-v1-spray-pattern"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |


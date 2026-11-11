# Per-question retrieval failures / unknown cases

Observed ranks are distinguished from unproven semantic-cause hypotheses.

## rag_001 — dense

T1059.001 refers to which Windows scripting environment?

Reference: PowerShell.
Answerable: True; type=english; language=en->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b1-1"], "recovered_below_cutoff": ["mitre_attack_v17_1-b1-1"], "first_relevant_rank": 10, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 2 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
| 3 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 4 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 5 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 6 | attack_t1021_006.md | `1f7eb169-9a12-5e59-b795-4ac0ce757da0` | none |
| 7 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | none |
| 8 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 9 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | none |
| 10 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | mitre_attack_v17_1-b1-1 |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 4, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 2 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 3 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 4 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | mitre_attack_v17_1-b1-1 |
| 5 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 6 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 7 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 8 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 9 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 10 | malware.md | `dba1b75f-5cf7-51a7-9393-5daee9064a55` | none |

## rag_002 — dense

What technique is assigned the ATT&CK identifier T1110?

Reference: Brute Force.
Answerable: True; type=english; language=en->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b20-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `3891aa62-ad0e-5f58-9b88-2525d547e7ac` | none |
| 2 | attack_t1027_010.md | `ff321312-4e9b-5253-9fe6-ad3a14a94f6e` | none |
| 3 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | none |
| 4 | attack_t1027_010.md | `de54c4ed-5ba6-55a0-9123-6ae0f1f3012b` | none |
| 5 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 6 | attack_t1027_010.md | `1a6dfdb7-1745-59ed-a476-c68e6e7e5283` | none |
| 7 | attack_t1027_010.md | `7e3f059c-4a68-5943-945a-a3e4eba18c8c` | none |
| 8 | attack_t1021_006.md | `1f7eb169-9a12-5e59-b795-4ac0ce757da0` | none |
| 9 | attack_t1027_010.md | `74e3d909-8b7d-5517-a2cf-a4491db86d5b` | none |
| 10 | attack_t1027_010.md | `3ff9fe68-110a-5623-b45d-5b6ddeb2ac79` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b20-1"], "recovered_below_cutoff": ["mitre_attack_v17_1-b20-1"], "first_relevant_rank": 7, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |
| 2 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 3 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 4 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 6 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 7 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | mitre_attack_v17_1-b20-1 |
| 8 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 9 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |

## rag_003 — dense

Which ATT&CK technique name corresponds to T1078?

Reference: Valid Accounts.
Answerable: True; type=english; language=en->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b33-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `3891aa62-ad0e-5f58-9b88-2525d547e7ac` | none |
| 2 | attack_t1027_010.md | `ff321312-4e9b-5253-9fe6-ad3a14a94f6e` | none |
| 3 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 4 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 5 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | none |
| 6 | attack_t1027_010.md | `de54c4ed-5ba6-55a0-9123-6ae0f1f3012b` | none |
| 7 | attack_t1021_006.md | `1f7eb169-9a12-5e59-b795-4ac0ce757da0` | none |
| 8 | attack_t1027_010.md | `7e3f059c-4a68-5943-945a-a3e4eba18c8c` | none |
| 9 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | none |
| 10 | attack_t1027_010.md | `1a6dfdb7-1745-59ed-a476-c68e6e7e5283` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b33-1"], "recovered_below_cutoff": ["mitre_attack_v17_1-b33-1"], "first_relevant_rank": 7, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |
| 2 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 3 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 4 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 5 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 6 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 7 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | mitre_attack_v17_1-b33-1 |
| 8 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 9 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |

## rag_004 — dense

Which OWASP WSTG test identifier covers SQL injection?

Reference: WSTG-INPV-05.
Answerable: True; type=english; language=en->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b1-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `8f963665-9197-5171-b935-f4831f318fad` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `cb9c27ff-2517-5b39-ade8-01646cb61694` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `bdf1376d-1c39-50d9-b566-5e44de790097` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `4af72c21-7282-5285-9e8c-5b6b2fe811d6` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `fb3488c4-e2da-5b86-a41b-81e9cf74aba9` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `657aa1ba-4fbd-5455-bc75-3900255de2f5` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `6d17d5d6-8cda-509c-954b-3f24873d4200` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `a59d4eeb-a57f-541f-975e-4448fea1228a` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `bf8e9aa0-0ea1-5e8f-8f79-d08f7aa7d335` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `be65717c-6d3e-5f5e-91be-653a7e09305b` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `fac8f961-fa7c-54de-afa1-3b07108faf9e` | owasp_wstg_v4_2_sql_injection-b1-1 |
| 2 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `1f917f30-46dd-5722-ba7f-5fead4783010` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `94a956a0-b8a9-5dde-b4bf-ba8b0f4b881b` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `d31d1d37-1832-547f-8426-6700a98884b3` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |

## rag_011 — dense

暴力破解告警的本地响应清单建议采取哪些措施？

Reference: 封禁可疑 IP、启用 MFA、调查受影响账户。
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["brute_force-b10-1", "brute_force-b11-2", "brute_force-b12-3"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 9 | sql_injection.md | `bacd8e44-864c-5be2-9f3a-07e3cadd5b04` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `fb972d7f-6f51-523a-9380-795e94fcd7ff` | none |
### parent
{"missing_evidence_ids": ["brute_force-b10-1", "brute_force-b11-2", "brute_force-b12-3"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 6 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `4924a677-7a32-5c43-9fe3-8d16cd327837` | none |

## rag_014 — dense

本地 SQL 注入知识库列出了哪些预防措施？

Reference: 预编译语句、输入验证、最小权限。
Answerable: True; type=mixed_terms; language=mixed->en

### child
{"missing_evidence_ids": ["sql_injection-b10-2", "sql_injection-b11-3", "sql_injection-b9-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `639cbbac-94ec-57dd-bd88-bb3945f9b42b` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f1262b92-a939-53d9-9818-4de70ba7115b` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `ca49cbce-b8d0-56f3-96ae-7826bc6e7a16` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `fb972d7f-6f51-523a-9380-795e94fcd7ff` | none |
### parent
{"missing_evidence_ids": ["sql_injection-b10-2", "sql_injection-b11-3", "sql_injection-b9-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 8 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4924a677-7a32-5c43-9fe3-8d16cd327837` | none |
| 10 | sql_injection.md | `a97cfdc3-337d-5574-9961-eb070faad246` | none |

## rag_020 — dense

When enumerating SQL-injection inputs, should hidden POST fields, HTTP headers and cookies be included?

Reference: Yes; test the input fields separately and consider headers and cookies.
Answerable: True; type=english; language=en->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b34-1"], "recovered_below_cutoff": ["owasp_wstg_v4_2_sql_injection-b34-1"], "first_relevant_rank": 8, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `d4ea4f63-f82a-5bc1-b774-0281046fbaa1` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `75753a76-01c0-59f0-a4cf-4b4abe270388` | none |
| 3 | sql_injection.md | `240fe162-b73e-543d-bf96-874fc7c27445` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `6953c28a-04dd-5a0d-a720-7a884e85255e` | none |
| 5 | sql_injection.md | `733dd27d-f7b2-5223-a487-c6d64e95c953` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `ca37ccd3-2bb8-531d-a521-0094c231c702` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `9e442b7d-ac16-5d43-8fe3-a3bfb4317505` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `169a848c-8109-55ab-9ffb-e2b303a46899` | owasp_wstg_v4_2_sql_injection-b34-1 |
| 9 | owasp_wstg_v4_2_sql_injection.md | `de56f54c-6d09-5e1f-bbd2-04fbe3b4f290` | none |
| 10 | sql_injection.md | `d886d741-718a-5eca-92c8-bd314df926b0` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 4, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 3 | sql_injection.md | `24d007a3-9ab6-5463-882c-40bf0052e8d7` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | owasp_wstg_v4_2_sql_injection-b34-1 |
| 5 | sql_injection.md | `1747a098-7f98-52a7-bd3b-c2c5669649f7` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `e11d7d74-a95a-56c1-94d6-942ac597fca6` | none |
| 9 | sql_injection.md | `a97cfdc3-337d-5574-9961-eb070faad246` | none |
| 10 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |

## rag_026 — dense

What is the exact production API key for the fictional Acme SOC deployment?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `3891aa62-ad0e-5f58-9b88-2525d547e7ac` | none |
| 2 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `a9d9c2d3-c190-5e1c-9cd3-22d07be16dd9` | none |
| 4 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 5 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
| 6 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 7 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 9 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 10 | attack_t1021_006.md | `1f7eb169-9a12-5e59-b795-4ac0ce757da0` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |
| 2 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2246b7fe-fdbd-5952-acc7-9faf7b777135` | none |
| 4 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 5 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 6 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 8 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `e5f6afee-116b-58f7-a9eb-f987bd03bd1d` | none |
| 10 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |

## rag_027 — dense

What indicators of compromise are documented for the fictional CVE-2099-99999?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `0054058a-7844-5b98-9ada-06310a90907e` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `323f29d6-5027-5df8-92c9-64da1831f634` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `9f1e9c27-159a-5573-942a-eac57ba52004` | none |
| 5 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `f8412402-0e29-56c2-8a82-7486b286897c` | none |
| 7 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 8 | continued_rules.pdf | `99eecf64-305c-506a-b474-55f527d252a6` | none |
| 9 | continued_rules.pdf | `b3f7c02e-cccf-5d9c-b2b3-788b10d19ec9` | none |
| 10 | attack_t1027_010.md | `7e3f059c-4a68-5943-945a-a3e4eba18c8c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 4 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 5 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 6 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 7 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 8 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 10 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |

## rag_028 — dense

在 2026-10-31 这次告警中，攻击者实际登录了哪些生产账户？

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `ff321312-4e9b-5253-9fe6-ad3a14a94f6e` | none |
| 2 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 3 | continued_rules.pdf | `99eecf64-305c-506a-b474-55f527d252a6` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 5 | continued_rules.pdf | `b3f7c02e-cccf-5d9c-b2b3-788b10d19ec9` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 7 | continued_rules.pdf | `b71a8739-7d34-54fe-8a03-2e010628fe27` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 10 | continued_rules.pdf | `b183339e-ab70-5672-9df8-a0d4b54a9958` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 2 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 3 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 7 | brute_force.md | `63630879-978b-548c-a918-111b10587b3c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 9 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |

## rag_029 — dense

Which vendor firmware command disables the fictional QuantumShield X900 audit engine?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `3891aa62-ad0e-5f58-9b88-2525d547e7ac` | none |
| 2 | attack_t1027_010.md | `7e3f059c-4a68-5943-945a-a3e4eba18c8c` | none |
| 3 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 4 | attack_t1027_010.md | `de54c4ed-5ba6-55a0-9123-6ae0f1f3012b` | none |
| 5 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | none |
| 6 | attack_t1027_010.md | `1a6dfdb7-1745-59ed-a476-c68e6e7e5283` | none |
| 7 | attack_t1027_010.md | `3ff9fe68-110a-5623-b45d-5b6ddeb2ac79` | none |
| 8 | attack_t1027_010.md | `7242f3d0-ddae-53c5-925d-aac6db694099` | none |
| 9 | attack_t1027_010.md | `9d5700b7-f9ff-5fbb-a376-529324034589` | none |
| 10 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |
| 2 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 3 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 4 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 5 | malware.md | `2e0da9f2-5784-57ce-9c9a-a155d9e459d2` | none |
| 6 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 7 | malware.md | `5e5e5068-0339-589e-9259-c6176968a43e` | none |
| 8 | malware.md | `dba1b75f-5cf7-51a7-9393-5daee9064a55` | none |
| 9 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 10 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |

## rag_030 — dense

What exact financial loss did the fictional ACME incident cause on 2026-10-31?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `0054058a-7844-5b98-9ada-06310a90907e` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `51188538-dd65-5146-bbd3-16f43a125923` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `f8412402-0e29-56c2-8a82-7486b286897c` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `9f1e9c27-159a-5573-942a-eac57ba52004` | none |
| 9 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `5d3f3c2b-f7aa-50e0-a23d-7eac886f576e` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 5 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 7 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 8 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 9 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 10 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |

## rag_031 — dense

为什么取证时没有发现新落地的程序文件，也不能排除系统自带脚本环境曾下载并运行过程序？

Reference: PowerShell can download executables and run them in memory without touching disk.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b7-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `fb972d7f-6f51-523a-9380-795e94fcd7ff` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b7-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 8 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |

## rag_032 — dense

用系统自带脚本环境连接另一台机器执行任务时，资料要求连接方具备什么权限？

Reference: Administrator permissions are required for PowerShell connections to remote systems.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b6-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `fd23cd73-8c34-56d7-9c3a-589ba1523814` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `35776641-36c8-55dc-8f7a-0a57647dcfb9` | none |
| 9 | brute_force.md | `248d9fc6-316f-5292-a86c-63d04e9b9451` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b6-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 8 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |

## rag_033 — dense

离职人员的身份被重新使用时，为什么这种活动可能更不容易被本人察觉？

Reference: The original account user is absent and cannot notice anomalous activity.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b35-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
| 6 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `de9a778a-4308-5260-9dd6-8226a6f05ef1` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `66f876e2-8cb6-5d98-81d0-2f756d6bf5ff` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b35-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 6 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |

## rag_034 — dense

攻击者已经拿到合法登录凭据时，还可能绕过资源上的哪类限制？

Reference: Compromised credentials may bypass access controls.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b34-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 3 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 4 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `35776641-36c8-55dc-8f7a-0a57647dcfb9` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 8 | continued_rules.pdf | `b183339e-ab70-5672-9df8-a0d4b54a9958` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b34-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 3 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 4 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |

## rag_035 — dense

大量身份各只收到少数几个常见口令的尝试，这种横着铺开的登录行为属于什么模式？

Reference: Password spraying uses one or a small list of common passwords against many accounts.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-spray-pattern"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | continued_rules.pdf | `b71a8739-7d34-54fe-8a03-2e010628fe27` | none |
| 3 | continued_rules.pdf | `b183339e-ab70-5672-9df8-a0d4b54a9958` | none |
| 4 | continued_rules.pdf | `b3f7c02e-cccf-5d9c-b2b3-788b10d19ec9` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 6 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 7 | continued_rules.pdf | `99eecf64-305c-506a-b474-55f527d252a6` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `c23b9ff1-d592-58b1-9874-0ac966216426` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 10 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
### parent
{"missing_evidence_ids": ["security-v1-spray-pattern"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 5 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |

## rag_036 — dense

把同一个候选口令轮流用于许多身份，而不是对单个身份反复更换口令，这样做是在规避什么？

Reference: Account lockouts caused by many guesses against one account.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-spray-lockout"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | continued_rules.pdf | `99eecf64-305c-506a-b474-55f527d252a6` | none |
| 2 | continued_rules.pdf | `b71a8739-7d34-54fe-8a03-2e010628fe27` | none |
| 3 | continued_rules.pdf | `b3f7c02e-cccf-5d9c-b2b3-788b10d19ec9` | none |
| 4 | continued_rules.pdf | `b183339e-ab70-5672-9df8-a0d4b54a9958` | none |
| 5 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 7 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `fd23cd73-8c34-56d7-9c3a-589ba1523814` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `334ff740-4d58-57b2-9eee-0f3a5e4fc543` | none |
| 10 | mitre_attack_v17_1.md | `3891aa62-ad0e-5f58-9b88-2525d547e7ac` | none |
### parent
{"missing_evidence_ids": ["security-v1-spray-lockout"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 3 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 6 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 10 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |

## rag_037 — dense

某个站点泄露的成对用户名和口令，为什么会被攻击者带到另一个站点再试一次？

Reference: Credential stuffing exploits overlap and users reusing passwords across personal and business accounts.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-stuffing-cause", "security-v1-stuffing-reuse"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `9f1e9c27-159a-5573-942a-eac57ba52004` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `c23b9ff1-d592-58b1-9874-0ac966216426` | none |
### parent
{"missing_evidence_ids": ["security-v1-stuffing-cause", "security-v1-stuffing-reuse"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 10 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |

## rag_038 — dense

攻击者不认识用户实际输入的密码字符，却拿着窃取的摘要完成认证，这属于哪种做法？

Reference: Pass the Hash authenticates as a user without the cleartext password.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-pth-auth"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 2 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 6 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 8 | continued_rules.pdf | `b183339e-ab70-5672-9df8-a0d4b54a9958` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `fb07fe0e-8f8e-545d-8e81-deb9e7a5a557` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
### parent
{"missing_evidence_ids": ["security-v1-pth-auth"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 2 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 5 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |

## rag_039 — dense

用户已经在主机上登录后，系统哪个安全进程的内存会保存可被窃取的凭据材料？

Reference: LSASS process memory stores credential materials after logon.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `35776641-36c8-55dc-8f7a-0a57647dcfb9` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `639cbbac-94ec-57dd-bd88-bb3945f9b42b` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
### parent
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |

## rag_040 — dense

攻击者把程序挂到用户登录时自动执行的位置，这个触发时机是什么？

Reference: It executes when a user logs in.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-run-logon"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 4 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `a7a5e4dd-a1de-5c84-b433-ee93011153e1` | none |
| 7 | sql_injection.md | `bacd8e44-864c-5be2-9f3a-07e3cadd5b04` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `5bbcdd61-fb5a-577d-8e3a-0e62e53635d3` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `c23b9ff1-d592-58b1-9874-0ac966216426` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
### parent
{"missing_evidence_ids": ["security-v1-run-logon"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 4 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |

## rag_041 — dense

借助用户登录自启动位置运行的程序，通常继承谁的身份上下文和权限？

Reference: The user context and associated account permissions.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-run-context"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 3 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `ca49cbce-b8d0-56f3-96ae-7826bc6e7a16` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `d196c1c5-c6ed-54eb-bc61-ac788896bf21` | none |
### parent
{"missing_evidence_ids": ["security-v1-run-context"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 3 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |

## rag_042 — dense

管理员希望把重复工作保存为可按顺序运行、还能写条件和循环的命令清单，哪种文件机制能做到？

Reference: Windows command-shell batch files such as .bat or .cmd.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-batch"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 3 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `35776641-36c8-55dc-8f7a-0a57647dcfb9` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `fab5b987-c7ca-5ed3-a706-4d88845eee74` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `de9a778a-4308-5260-9dd6-8226a6f05ef1` | none |
### parent
{"missing_evidence_ids": ["security-v1-batch"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 3 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 9 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |

## rag_043 — dense

办公文档为什么能像小程序一样，在事件触发时自动执行主机任务？

Reference: VBA is event-driven and lets Office documents contain task-automation macros.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `5d3f3c2b-f7aa-50e0-a23d-7eac886f576e` | none |
### parent
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |

## rag_044 — dense

一种常被当成网页专用的脚本语言，能否在没有浏览器页面的运行环境里执行？

Reference: Yes; JavaScript can execute in runtime environments outside the browser.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-js-runtime"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 3 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 4 | sql_injection.md | `bacd8e44-864c-5be2-9f3a-07e3cadd5b04` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
### parent
{"missing_evidence_ids": ["security-v1-js-runtime"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 4 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 9 | brute_force.md | `63630879-978b-548c-a918-111b10587b3c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |

## rag_045 — dense

不打开浏览器窗口也能运行网页应用格式的独立程序，资料指的是哪个系统工具？

Reference: Mshta.exe executes HTA files; HTAs run outside the browser.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-mshta-files", "security-v1-mshta-outside"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 4 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `3a293e8f-167b-5fc6-a719-bf0289f0f43c` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `c23b9ff1-d592-58b1-9874-0ac966216426` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `fd23cd73-8c34-56d7-9c3a-589ba1523814` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `a7a5e4dd-a1de-5c84-b433-ee93011153e1` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
### parent
{"missing_evidence_ids": ["security-v1-mshta-files", "security-v1-mshta-outside"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 4 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |

## rag_046 — dense

攻击者借用合法账号连接远程管理机制后，会以哪个登录身份执行后续操作？

Reference: WinRM interactions can perform actions as the logged-on user.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-winrm-user"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 2 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `fb07fe0e-8f8e-545d-8e81-deb9e7a5a557` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b980b840-2a30-5f7c-8b3d-2ae5e4981b14` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `c23b9ff1-d592-58b1-9874-0ac966216426` | none |
### parent
{"missing_evidence_ids": ["security-v1-winrm-user"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 2 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |

## rag_047 — dense

远程管理机制除了启动程序，还允许对目标系统的哪两类配置进行修改？

Reference: WinRM can modify the Registry and services.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 3 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `c23b9ff1-d592-58b1-9874-0ac966216426` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `ca49cbce-b8d0-56f3-96ae-7826bc6e7a16` | none |
| 6 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `d2d7230b-27db-5058-9eb1-483838f6477d` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
### parent
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 3 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 6 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `8f58fdb9-5926-566a-924d-e94cf16cf2ca` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |

## rag_048 — dense

不是向用户登录目录放文件，而是借助系统服务管理接口来启动载荷，这对应什么执行机制？

Reference: Service Execution abuses the Windows service control manager.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-service-manager"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 5 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 8 | continued_rules.pdf | `b183339e-ab70-5672-9df8-a0d4b54a9958` | none |
| 9 | continued_rules.pdf | `b71a8739-7d34-54fe-8a03-2e010628fe27` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
### parent
{"missing_evidence_ids": ["security-v1-service-manager"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 5 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 9 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |

## rag_049 — dense

数据库结果不直接出现在页面中时，测试者可以通过什么观察方式重建信息？

Reference: Inferential/blind injection sends requests and observes database behaviour.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 2 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `5d3f3c2b-f7aa-50e0-a23d-7eac886f576e` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `f8412402-0e29-56c2-8a82-7486b286897c` | none |
### parent
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": ["owasp_wstg_v4_2_sql_injection-b17-1"], "first_relevant_rank": 6, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 2 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | owasp_wstg_v4_2_sql_injection-b17-1 |
| 7 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 9 | malware.md | `5e5e5068-0339-589e-9259-c6176968a43e` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |

## rag_050 — dense

查询结果不沿着提交输入的页面返回，而是另走一条通信通道，这属于哪种取数方式？

Reference: Out-of-band SQL injection retrieves data through a different channel.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b16-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `79948902-3a47-5e8e-aa27-ccb4ea588690` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `a7a5e4dd-a1de-5c84-b433-ee93011153e1` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | owasp_wstg_v4_2_sql_injection-b16-2 |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |

## rag_051 — dense

梳理可能进入数据库查询的入口时，只查看可见输入框够不够，还应考虑哪些隐藏或附带的请求内容？

Reference: Include hidden POST fields, HTTP headers and cookies, and test input fields separately.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b34-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 3 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 5 | continued_rules.pdf | `b71a8739-7d34-54fe-8a03-2e010628fe27` | none |
| 6 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 8 | continued_rules.pdf | `b183339e-ab70-5672-9df8-a0d4b54a9958` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 10 | continued_rules.pdf | `b3f7c02e-cccf-5d9c-b2b3-788b10d19ec9` | none |
### parent
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b34-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 2 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 5 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |

## rag_052 — dense

恢复工作尚未结束时，已经发现的改进经验应当什么时候分享，而不是等待什么节点？

Reference: Share lessons as soon as identified; do not delay until recovery concludes.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["nist_sp80061r3_pp10-12-b38-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `79948902-3a47-5e8e-aa27-ccb4ea588690` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 8 | brute_force.md | `248d9fc6-316f-5292-a86c-63d04e9b9451` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `66f876e2-8cb6-5d98-81d0-2f756d6bf5ff` | none |
### parent
{"missing_evidence_ids": ["nist_sp80061r3_pp10-12-b38-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 5 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |

## rag_053 — dense

为什么一本固定出版物不再适合维护所有事件处置的操作细节？

Reference: Response details change often and vary across technologies, environments and organizations.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["nist_sp80061r3_pp10-12-b14-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `d196c1c5-c6ed-54eb-bc61-ac788896bf21` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `db855a7f-a6af-5262-aeec-9d096657ceb0` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `36828c5a-65d6-5584-bffb-365d2bea4476` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ca49cbce-b8d0-56f3-96ae-7826bc6e7a16` | none |
### parent
{"missing_evidence_ids": ["nist_sp80061r3_pp10-12-b14-1"], "recovered_below_cutoff": ["nist_sp80061r3_pp10-12-b14-1"], "first_relevant_rank": 9, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 6 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | nist_sp80061r3_pp10-12-b14-1 |
| 10 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |

## rag_054 — dense

恶意软件事件处理完后，已受影响的认证材料和用于恢复的数据副本分别该如何处理？

Reference: Reset compromised credentials and restore from clean backups.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["malware-b17-1", "malware-b18-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `5d3f3c2b-f7aa-50e0-a23d-7eac886f576e` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `0054058a-7844-5b98-9ada-06310a90907e` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `51188538-dd65-5146-bbd3-16f43a125923` | none |
### parent
{"missing_evidence_ids": ["malware-b17-1", "malware-b18-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 8 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |

## rag_059 — dense

WinRM 不只是 PowerShell 命令名，它在系统里同时代表哪两种东西？

Reference: Both a Windows service and a remote interaction protocol.
Answerable: True; type=mixed_terms; language=mixed->en

### child
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": ["security-v1-winrm-service"], "first_relevant_rank": 6, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 2 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 3 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 4 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 5 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | none |
| 6 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | security-v1-winrm-service |
| 7 | attack_t1021_006.md | `1f7eb169-9a12-5e59-b795-4ac0ce757da0` | none |
| 8 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 9 | attack_t1027_010.md | `ff321312-4e9b-5253-9fe6-ad3a14a94f6e` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 3, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 2 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 3 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | security-v1-winrm-service |
| 4 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 5 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 8 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |

## rag_066 — dense

Base64 或 URL encoding 在 Command Obfuscation 中起什么作用？

Reference: They are built-in forms of obfuscation that make command strings and patterns harder to signature and analyze.
Answerable: True; type=mixed_terms; language=mixed->en

### child
{"missing_evidence_ids": ["security-v1-obfuscation-purpose"], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | security-v1-obfuscation-encoding |
| 2 | attack_t1027_010.md | `ff321312-4e9b-5253-9fe6-ad3a14a94f6e` | none |
| 3 | attack_t1027_010.md | `b76c5fc1-dc47-521d-b75c-a45527b3546c` | none |
| 4 | attack_t1027_010.md | `3ff9fe68-110a-5623-b45d-5b6ddeb2ac79` | none |
| 5 | attack_t1027_010.md | `7242f3d0-ddae-53c5-925d-aac6db694099` | none |
| 6 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 7 | attack_t1027_010.md | `74e3d909-8b7d-5517-a2cf-a4491db86d5b` | none |
| 8 | attack_t1027_010.md | `1a6dfdb7-1745-59ed-a476-c68e6e7e5283` | none |
| 9 | attack_t1027_010.md | `4c1af995-09cd-562a-be2e-dd98d0292492` | none |
| 10 | attack_t1027_010.md | `7e3f059c-4a68-5943-945a-a3e4eba18c8c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | security-v1-obfuscation-purpose, security-v1-obfuscation-encoding |
| 2 | owasp_wstg_v4_2_sql_injection.md | `4924a677-7a32-5c43-9fe3-8d16cd327837` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `04903bb6-9c4f-597e-afa2-b3756415cb82` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |

## rag_068 — dense

有没有办法让一个程序在用户开始新的桌面会话时自己再次运行，而不需要用户亲手启动它？

Reference: A Registry run key or startup-folder entry launches the referenced program when the user logs in.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-run-logon"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 4 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `fb07fe0e-8f8e-545d-8e81-deb9e7a5a557` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `fb972d7f-6f51-523a-9380-795e94fcd7ff` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `ca49cbce-b8d0-56f3-96ae-7826bc6e7a16` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
### parent
{"missing_evidence_ids": ["security-v1-run-logon"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 4 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |

## rag_070 — dense

为什么攻击者会把一份很短的猜测清单分散用于许多身份，而不把所有尝试押在同一个身份上？

Reference: To avoid account lockouts associated with many password guesses against a single account.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-spray-lockout"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `7496f486-e95f-51d8-b356-a7fe754b8591` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 5 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `be4eb270-44e3-53c2-b5f3-98b1ce71f9cb` | none |
| 8 | brute_force.md | `df7d8241-91d9-5105-802e-6f633e677246` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `a5e218dc-32d0-531c-97c3-5935ed69482a` | none |
| 10 | brute_force.md | `248d9fc6-316f-5292-a86c-63d04e9b9451` | none |
### parent
{"missing_evidence_ids": ["security-v1-spray-lockout"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 5 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `3bdc9d27-275e-58ee-8caa-ef37f2997028` | none |
| 8 | brute_force.md | `63630879-978b-548c-a918-111b10587b3c` | none |
| 9 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |

## rag_072 — dense

办公文件原本只是内容载体，哪种内置能力能让它在特定事件发生时自动执行主机任务？

Reference: VBA macros in Office documents can automate host tasks.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `ca49cbce-b8d0-56f3-96ae-7826bc6e7a16` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `fb07fe0e-8f8e-545d-8e81-deb9e7a5a557` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `5bbcdd61-fb5a-577d-8e3a-0e62e53635d3` | none |
### parent
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |

## rag_074 — dense

不去猜用户的口令，而是寻找已经登录的会话留下的秘密，应查看哪里，又需要哪类身份才能提取？

Reference: Credential materials are stored in LSASS process memory and can be harvested by an administrative user or SYSTEM.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-lsass-memory", "security-v1-lsass-rights"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 3 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `9f1e9c27-159a-5573-942a-eac57ba52004` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
### parent
{"missing_evidence_ids": ["security-v1-lsass-memory", "security-v1-lsass-rights"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |

## rag_076 — dense

What account attack tries the same few common passwords across identities to avoid per-account lockout?

Reference: Password spraying.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [4], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 2 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | security-v1-spray-pattern, security-v1-spray-lockout |
| 3 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 4 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 5 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 6 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 7 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 8 | brute_force.md | `248d9fc6-316f-5292-a86c-63d04e9b9451` | none |
| 9 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | none |
| 10 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [4], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 2 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | security-v1-spray-pattern, security-v1-spray-lockout |
| 3 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 4 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 5 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 6 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 7 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 8 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 9 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 10 | brute_force.md | `cb2c87f1-0241-5ad4-a053-5168b2cf5eef` | none |

## rag_077 — dense

攻击者已经拿到外站泄露的成对账号密码，再利用用户复用习惯登录目标；这与轮试常见口令的模式如何区分？

Reference: Credential stuffing uses breach-dump credentials and password overlap.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-stuffing-cause", "security-v1-stuffing-reuse"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 6 | continued_rules.pdf | `b71a8739-7d34-54fe-8a03-2e010628fe27` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 8 | continued_rules.pdf | `99eecf64-305c-506a-b474-55f527d252a6` | none |
| 9 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 10 | continued_rules.pdf | `b3f7c02e-cccf-5d9c-b2b3-788b10d19ec9` | none |
### parent
{"missing_evidence_ids": ["security-v1-stuffing-cause", "security-v1-stuffing-reuse"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 6 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 7 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 8 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 9 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |

## rag_078 — dense

Which technique uses a stolen hash to authenticate directly rather than cracking it back into a password?

Reference: Pass the Hash authenticates without the cleartext password.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | security-v1-pth-auth |
| 2 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 3 | brute_force.md | `0caddcca-4cdf-5ae3-97d7-c39c4d5cd460` | none |
| 4 | brute_force.md | `df7d8241-91d9-5105-802e-6f633e677246` | none |
| 5 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | none |
| 6 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 7 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 8 | brute_force.md | `248d9fc6-316f-5292-a86c-63d04e9b9451` | none |
| 9 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 10 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | security-v1-pth-auth |
| 2 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 3 | brute_force.md | `cb2c87f1-0241-5ad4-a053-5168b2cf5eef` | none |
| 4 | brute_force.md | `63630879-978b-548c-a918-111b10587b3c` | none |
| 5 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 6 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 7 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 8 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 9 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 10 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |

## rag_079 — dense

分析目标是获取已登录会话留下的内存凭据，而不是使用现成摘要去认证；应该聚焦哪个安全进程？

Reference: LSASS process memory.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `639cbbac-94ec-57dd-bd88-bb3945f9b42b` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f1262b92-a939-53d9-9818-4de70ba7115b` | none |
### parent
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |

## rag_080 — dense

Which language mechanism best fits event-driven macros embedded in Office documents rather than webpage scripts?

Reference: Visual Basic for Applications (VBA) macros.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | security-v1-vba-event, security-v1-vba-macros |
| 2 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 3 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 4 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 5 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 6 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
| 7 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | none |
| 8 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 9 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `0054058a-7844-5b98-9ada-06310a90907e` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | security-v1-vba-event, security-v1-vba-macros |
| 2 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 3 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 4 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 5 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 6 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |

## rag_081 — dense

线索明确是由系统脚本引擎解释的微软脚本实现，而非办公文档宏；应找哪个实现？

Reference: JScript.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-js-engine"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 7 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f1262b92-a939-53d9-9818-4de70ba7115b` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `d196c1c5-c6ed-54eb-bc61-ac788896bf21` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
### parent
{"missing_evidence_ids": ["security-v1-js-engine"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 6 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |

## rag_082 — dense

Which mechanism uses batch files with sequential commands and loops rather than PowerShell cmdlets?

Reference: Windows command-shell batch files (.bat or .cmd).
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2, 3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | security-v1-batch |
| 2 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 3 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 4 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | none |
| 5 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 6 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 7 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | none |
| 8 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
| 9 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
| 10 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | security-v1-batch |
| 2 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 3 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 4 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 5 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 6 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 8 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 9 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 10 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |

## rag_083 — dense

需要远程修改注册表和服务，线索指向一种同名的系统服务与协议，而非仅仅本地命令解释器；它是什么？

Reference: Windows Remote Management (WinRM).
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `681d8f2b-ffdc-5f1e-9c2a-acb11f044369` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `fdda8ead-332c-5649-baf1-de97e5c5eb2b` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `35776641-36c8-55dc-8f7a-0a57647dcfb9` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `bf089b6c-ca1d-5fe1-a14d-11ea491056c1` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `2214dfb2-d620-5744-9fa7-8e36c4669138` | none |
### parent
{"missing_evidence_ids": ["security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `4924a677-7a32-5c43-9fe3-8d16cd327837` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |

## rag_084 — dense

What persistence location executes a referenced program at user logon with that user permissions rather than via a temporary remote service?

Reference: Registry run keys or startup folders.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | security-v1-run-logon, security-v1-run-context |
| 2 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | none |
| 3 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 4 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 5 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 6 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 7 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 8 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 9 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 10 | attack_t1021_006.md | `1f7eb169-9a12-5e59-b795-4ac0ce757da0` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | security-v1-run-logon, security-v1-run-context |
| 2 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 3 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 4 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 5 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 6 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 7 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 8 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 9 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 10 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |

## rag_085 — dense

载荷通过服务管理器的临时服务运行，不是等用户下次登录；资料中对应什么执行方式？

Reference: Service Execution; PsExec can create a temporary service through the SCM API.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-service-psexec"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `903409e5-4e5e-5945-b416-dda99afb1f9d` | none |
| 3 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 4 | continued_rules.pdf | `99eecf64-305c-506a-b474-55f527d252a6` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 6 | continued_rules.pdf | `b71a8739-7d34-54fe-8a03-2e010628fe27` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `0c9c3d8b-b699-5e3e-80d9-7ec8ceaf237b` | none |
| 9 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
### parent
{"missing_evidence_ids": ["security-v1-service-psexec"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 3 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 4 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 9 | brute_force.md | `63630879-978b-548c-a918-111b10587b3c` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |

## rag_086 — dense

Which system scripting environment can download and execute programs in memory without touching disk, unlike batch-file or logon-entry mechanisms?

Reference: PowerShell.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 3, "hard_negative_ranks": [1], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 2 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 3 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | mitre_attack_v17_1-b7-1 |
| 4 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 5 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 6 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 7 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 8 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 9 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | none |
| 10 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [1, 5], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 2 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | mitre_attack_v17_1-b7-1 |
| 3 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 4 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 5 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 6 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 7 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 8 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 9 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 10 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |

## rag_087 — dense

现象是把原来可识别的命令改写成难以签名的编码或字符串形式，而不是换一个脚本宿主；这描述哪种目的？

Reference: Command obfuscation impedes signature matching and analysis.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-obfuscation-purpose"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ea97e298-d534-5488-8103-036850028884` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `fdda8ead-332c-5649-baf1-de97e5c5eb2b` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 7 | brute_force.md | `248d9fc6-316f-5292-a86c-63d04e9b9451` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `636016b8-67f1-54d7-b042-dac0d9d6ed1a` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
### parent
{"missing_evidence_ids": ["security-v1-obfuscation-purpose"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 5 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 7 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `e1fbe1fe-fbc1-5b52-9433-76c68fbd4284` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |

## rag_089 — dense

目标将查询结果交给另一条通信链路，而不是直接显示在提交输入的原页面；应归为哪一类？

Reference: Out-of-band.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b16-2"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 3 | continued_rules.pdf | `b71a8739-7d34-54fe-8a03-2e010628fe27` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 7 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 8 | continued_rules.pdf | `40163002-3c0d-57da-ac11-e6477be5396e` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `5af33663-17ac-5be9-995e-d356ff4ac301` | none |
| 10 | continued_rules.pdf | `b183339e-ab70-5672-9df8-a0d4b54a9958` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 4, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 3 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | owasp_wstg_v4_2_sql_injection-b16-2 |
| 5 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 7 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |

## rag_090 — dense

Which trusted Windows utility executes standalone HTA files rather than Office document macros?

Reference: Mshta.exe.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | security-v1-mshta-files, security-v1-mshta-outside |
| 2 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
| 3 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 4 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | none |
| 5 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 6 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 7 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 8 | attack_t1027_010.md | `9d5700b7-f9ff-5fbb-a376-529324034589` | none |
| 9 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 10 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | security-v1-mshta-files, security-v1-mshta-outside |
| 2 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 3 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 4 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 5 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 6 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 7 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 8 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 9 | malware.md | `2e0da9f2-5784-57ce-9c9a-a155d9e459d2` | none |
| 10 | malware.md | `dba1b75f-5cf7-51a7-9393-5daee9064a55` | none |

## rag_091 — dense

我们租户当前到底连续失败几次才会锁定账号，锁定持续多少分钟？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca49cbce-b8d0-56f3-96ae-7826bc6e7a16` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 4 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `6b8bd0de-bd01-5b33-a4dd-a5aa583c026e` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `3a293e8f-167b-5fc6-a719-bf0289f0f43c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `7496f486-e95f-51d8-b356-a7fe754b8591` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `a7a5e4dd-a1de-5c84-b433-ee93011153e1` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 3 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `04903bb6-9c4f-597e-afa2-b3756415cb82` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |

## rag_092 — dense

这次内存采集实际提取到了哪些域用户的密码摘要？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 2 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `5bbcdd61-fb5a-577d-8e3a-0e62e53635d3` | none |
| 5 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `0e8b159b-cc64-5e9f-9b77-8ecdc170643e` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `a7a5e4dd-a1de-5c84-b433-ee93011153e1` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b63df3a0-50c3-5f9a-8a7f-6c7bce42ca5b` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 2 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 4 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `fc70da0c-00d2-524b-95ce-7a88039f1f71` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | brute_force.md | `63630879-978b-548c-a918-111b10587b3c` | none |

## rag_093 — dense

终端 SEC-WS-17 上的登录自启动条目是谁在什么时间写入的？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 2 | attack_t1027_010.md | `7e3f059c-4a68-5943-945a-a3e4eba18c8c` | none |
| 3 | mitre_attack_v17_1.md | `3891aa62-ad0e-5f58-9b88-2525d547e7ac` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `60cbffe6-85b9-5b71-a0f8-b0e773b92703` | none |
| 5 | attack_t1027_010.md | `ff321312-4e9b-5253-9fe6-ad3a14a94f6e` | none |
| 6 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `a7a5e4dd-a1de-5c84-b433-ee93011153e1` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 10 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 2 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 3 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 5 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 8 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |

## rag_094 — dense

昨晚触发编码脚本告警的外部来源地址具体是多少？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `bf089b6c-ca1d-5fe1-a14d-11ea491056c1` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `4924a677-7a32-5c43-9fe3-8d16cd327837` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 9 | sql_injection.md | `18d3fb9f-7256-5929-96b2-d41e5d7fe257` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |

## rag_095 — dense

本次主机隔离是否已经由值班人员实际执行成功？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `b63df3a0-50c3-5f9a-8a7f-6c7bce42ca5b` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `a7a5e4dd-a1de-5c84-b433-ee93011153e1` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `07bf8554-7db8-5e0d-a624-04ef13b24e0d` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `e096b7c4-0c24-5643-9f4c-2ba6173868bb` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `4924a677-7a32-5c43-9fe3-8d16cd327837` | none |

## rag_097 — dense

请分别说明用户登录自启动程序的触发时机，以及远程管理机制可修改的两类系统配置，不要把两种机制混为一谈。

Reference: Run-key/startup programs execute at user logon; WinRM can modify the Registry and services.
Answerable: True; type=multi_document; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-run-logon", "security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 2 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `faf3a62e-8a1a-51fb-8880-b5efa25dd6d8` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `fb972d7f-6f51-523a-9380-795e94fcd7ff` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `35776641-36c8-55dc-8f7a-0a57647dcfb9` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `79948902-3a47-5e8e-aa27-ccb4ea588690` | none |
### parent
{"missing_evidence_ids": ["security-v1-run-logon", "security-v1-winrm-service"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 2 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `04903bb6-9c4f-597e-afa2-b3756415cb82` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 9 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |

## rag_098 — dense

针对恶意软件事件，网络、认证材料和恢复副本应分别如何处理；已经发现的经验教训是否要等恢复结束才分享？

Reference: Isolate affected systems from the network, reset compromised credentials and restore clean backups; share identified lessons promptly rather than wait for recovery completion.
Answerable: True; type=multi_document; language=zh->en

### child
{"missing_evidence_ids": ["malware-b14-1", "malware-b17-1", "malware-b18-2", "nist_sp80061r3_pp10-12-b38-1"], "recovered_below_cutoff": ["nist_sp80061r3_pp10-12-b38-1"], "first_relevant_rank": 9, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `28d6194d-ece9-50be-b310-cc54cd624ee8` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `2fc6b299-365e-56c9-8c6a-8e3b4f4f17a9` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `5d3f3c2b-f7aa-50e0-a23d-7eac886f576e` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `51188538-dd65-5146-bbd3-16f43a125923` | nist_sp80061r3_pp10-12-b38-1 |
| 10 | nist_sp80061r3_pp10-12.pdf | `5346b998-ec8f-5fc3-a273-44d80e07adbb` | none |
### parent
{"missing_evidence_ids": ["malware-b14-1", "malware-b17-1", "malware-b18-2"], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | nist_sp80061r3_pp10-12-b38-1 |
| 3 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | mitre_attack_v17_1.md | `67b47af1-6e6e-5cdf-96d4-a6bd6ab20704` | none |

## rag_100 — dense

先说明少量常见口令遍历许多身份的行为模式，再列出本地暴力破解清单的三项建议；不要声称每项措施与某个指标一一对应。

Reference: Password spraying uses a small password set against many accounts; the local guide recommends blocking suspicious IPs, enabling MFA and investigating affected accounts.
Answerable: True; type=multi_document; language=zh->en

### child
{"missing_evidence_ids": ["brute_force-b10-1", "brute_force-b11-2", "brute_force-b12-3", "security-v1-spray-pattern"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `1a43bb15-96ea-5914-a23a-9f3eae7429fd` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `2a938672-f36c-520b-a4fc-7e36f4551d8f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `af10073a-dbd3-5fdc-9c33-cb53c558f9ce` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `fb972d7f-6f51-523a-9380-795e94fcd7ff` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `33a462ea-c98f-5d31-9142-57c449cfe98b` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `a945c207-d4d9-5556-823a-859310f2ba9d` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
### parent
{"missing_evidence_ids": ["brute_force-b10-1", "brute_force-b11-2", "brute_force-b12-3", "security-v1-spray-pattern"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 9 | continued_rules.pdf | `02654193-7e2c-5aea-b7b0-922f0186be66` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |


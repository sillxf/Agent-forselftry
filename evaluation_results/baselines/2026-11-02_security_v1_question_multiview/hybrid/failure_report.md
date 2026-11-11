# Per-question retrieval failures, context noise and unknown cases

Observed ranks are distinguished from unproven semantic-cause hypotheses.

## rag_004 — hybrid

Which OWASP WSTG test identifier covers SQL injection?

Reference: WSTG-INPV-05.
Answerable: True; type=english; language=en->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b1-1"], "recovered_below_cutoff": ["owasp_wstg_v4_2_sql_injection-b1-1"], "first_relevant_rank": 8, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `8f2bcaec-cf6c-563e-85ed-da0808c770a5` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `be65717c-6d3e-5f5e-91be-653a7e09305b` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `9e442b7d-ac16-5d43-8fe3-a3bfb4317505` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `5cb47030-8296-5fe2-9c15-c853b4d2853d` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `09e2e59b-f74a-59bc-8af7-2bb3520c80e4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `5b63ec50-4163-5b18-8db0-b4cab4456aab` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `78f2651b-4f31-5652-9aec-d673b43a6fc1` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `61bc522d-f34a-5400-b47a-c5aeaacfe63c` | owasp_wstg_v4_2_sql_injection-b1-1 |
| 9 | owasp_wstg_v4_2_sql_injection.md | `3a293e8f-167b-5fc6-a719-bf0289f0f43c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `62b73a03-ebc8-5438-afbb-eb7074f8084f` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 5, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `1f917f30-46dd-5722-ba7f-5fead4783010` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `fac8f961-fa7c-54de-afa1-3b07108faf9e` | owasp_wstg_v4_2_sql_injection-b1-1 |
| 6 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `fc70da0c-00d2-524b-95ce-7a88039f1f71` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |

## rag_009 — hybrid

How can a tester infer database information when no data is returned directly?

Reference: Use inferential/blind SQL injection: send requests and observe database behaviour.
Answerable: True; type=paraphrase; language=en->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": ["owasp_wstg_v4_2_sql_injection-b17-1"], "first_relevant_rank": 6, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `79948902-3a47-5e8e-aa27-ccb4ea588690` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `9cc089f1-2aef-5cf3-a59c-485a5cc2d896` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `62b73a03-ebc8-5438-afbb-eb7074f8084f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `a00dba3e-b156-5c3f-983a-a3fb893eaa08` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `169a848c-8109-55ab-9ffb-e2b303a46899` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `9e442b7d-ac16-5d43-8fe3-a3bfb4317505` | owasp_wstg_v4_2_sql_injection-b17-1 |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f26f162c-7084-5cbf-adff-3870315cb474` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `0c4540cf-878d-5a57-a41a-a0fc9a97b554` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ca37ccd3-2bb8-531d-a521-0094c231c702` | none |
### parent
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": ["owasp_wstg_v4_2_sql_injection-b17-1"], "first_relevant_rank": 6, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `b2e6391b-7beb-5336-a631-dcad4a7ba57f` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | owasp_wstg_v4_2_sql_injection-b17-1 |
| 7 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |

## rag_014 — hybrid

本地 SQL 注入知识库列出了哪些预防措施？

Reference: 预编译语句、输入验证、最小权限。
Answerable: True; type=mixed_terms; language=mixed->en

### child
{"missing_evidence_ids": ["sql_injection-b10-2", "sql_injection-b11-3", "sql_injection-b9-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `f62ed3d7-e9e3-52c1-90a2-e41f8c35889e` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `de56f54c-6d09-5e1f-bbd2-04fbe3b4f290` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `c100262e-7d15-5b2e-9ebb-a90d542ddd8d` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `1c724127-7778-5142-aa2e-c55dede8f4d1` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `32e06c82-2ca5-5efa-ac0a-399e886d3560` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `08d26c33-4ad6-50dd-bbe9-3b1b66d3a9ec` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `5cb47030-8296-5fe2-9c15-c853b4d2853d` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `5b63ec50-4163-5b18-8db0-b4cab4456aab` | none |
| 9 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `59a6eb4c-a27c-584e-9b19-afd65c4a5954` | none |
### parent
{"missing_evidence_ids": ["sql_injection-b10-2", "sql_injection-b11-3", "sql_injection-b9-1"], "recovered_below_cutoff": ["sql_injection-b10-2", "sql_injection-b11-3", "sql_injection-b9-1"], "first_relevant_rank": 8, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `8f58fdb9-5926-566a-924d-e94cf16cf2ca` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `e11d7d74-a95a-56c1-94d6-942ac597fca6` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `e5f6afee-116b-58f7-a9eb-f987bd03bd1d` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 5 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `018d356b-9b08-5b49-abf4-6e879c19da16` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 8 | sql_injection.md | `1747a098-7f98-52a7-bd3b-c2c5669649f7` | sql_injection-b9-1, sql_injection-b10-2, sql_injection-b11-3 |
| 9 | sql_injection.md | `24d007a3-9ab6-5463-882c-40bf0052e8d7` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |

## rag_026 — hybrid

What is the exact production API key for the fictional Acme SOC deployment?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `a7c9578a-5ca7-5361-85e1-913cf7e59b7a` | none |
| 2 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 3 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
| 4 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `f26f162c-7084-5cbf-adff-3870315cb474` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `4f1ddf29-046a-5279-b643-36ab6a0e0533` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `70e41073-8104-5d67-b28d-7840c9d3f4b7` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `9e442b7d-ac16-5d43-8fe3-a3bfb4317505` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `ea97e298-d534-5488-8103-036850028884` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `2b56f778-7119-5e36-a10b-c50f3f208a19` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `fc70da0c-00d2-524b-95ce-7a88039f1f71` | none |
| 2 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 3 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 4 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |

## rag_027 — hybrid

What indicators of compromise are documented for the fictional CVE-2099-99999?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 2 | malware.md | `0569ed09-a27c-54a6-8ea4-de7a6b02b210` | none |
| 3 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 4 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `db9e07ec-406e-565c-9dc6-1be1a4500133` | none |
| 6 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `0054058a-7844-5b98-9ada-06310a90907e` | none |
| 8 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `9f1e9c27-159a-5573-942a-eac57ba52004` | none |
| 10 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 2 | malware.md | `5e5e5068-0339-589e-9259-c6176968a43e` | none |
| 3 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 4 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `73d0c122-c86f-5e3e-9f0e-f865f353b504` | none |
| 6 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 8 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `1f917f30-46dd-5722-ba7f-5fead4783010` | none |

## rag_028 — hybrid

在 2026-10-31 这次告警中，攻击者实际登录了哪些生产账户？

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 2 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 3 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 4 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 5 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `e9a4d66f-e907-5cd4-ab00-a72e238a1d9e` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `9f1e9c27-159a-5573-942a-eac57ba52004` | none |
| 8 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 9 | attack_t1027_010.md | `4c1af995-09cd-562a-be2e-dd98d0292492` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `2c11415b-8b9d-5985-9a68-cb93d5e0b9b9` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 2 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 3 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 4 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 6 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 7 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 8 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b2e6391b-7beb-5336-a631-dcad4a7ba57f` | none |
| 10 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |

## rag_029 — hybrid

Which vendor firmware command disables the fictional QuantumShield X900 audit engine?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | none |
| 2 | attack_t1027_010.md | `7242f3d0-ddae-53c5-925d-aac6db694099` | none |
| 3 | attack_t1027_010.md | `1a6dfdb7-1745-59ed-a476-c68e6e7e5283` | none |
| 4 | attack_t1027_010.md | `3ff9fe68-110a-5623-b45d-5b6ddeb2ac79` | none |
| 5 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 6 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 7 | attack_t1027_010.md | `b76c5fc1-dc47-521d-b75c-a45527b3546c` | none |
| 8 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
| 9 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 10 | attack_t1027_010.md | `74e3d909-8b7d-5517-a2cf-a4491db86d5b` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 2 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 3 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 4 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `04903bb6-9c4f-597e-afa2-b3756415cb82` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `2bacdf0d-4284-5d41-a0f4-6488d1895dbc` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |

## rag_030 — hybrid

What exact financial loss did the fictional ACME incident cause on 2026-10-31?

Reference: Insufficient evidence in this corpus.
Answerable: False; type=unanswerable; language=en->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `f8412402-0e29-56c2-8a82-7486b286897c` | none |
| 2 | nist_sp80061r3_pp10-12.pdf | `0054058a-7844-5b98-9ada-06310a90907e` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `9f1e9c27-159a-5573-942a-eac57ba52004` | none |
| 4 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `51188538-dd65-5146-bbd3-16f43a125923` | none |
| 6 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 7 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 8 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `41f65c20-f291-56ad-b718-27ef214ac113` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `50c620e8-8f3c-5909-982f-4a087dcd36f2` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 2 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 3 | nist_sp80061r3_pp10-12.pdf | `fdc3f284-d67e-56da-8d91-55a30dca7346` | none |
| 4 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 5 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `152a78fd-3a03-5190-9903-eb307205f500` | none |
| 8 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 10 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |

## rag_031 — hybrid

为什么取证时没有发现新落地的程序文件，也不能排除系统自带脚本环境曾下载并运行过程序？

Reference: PowerShell can download executables and run them in memory without touching disk.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["mitre_attack_v17_1-b7-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `75753a76-01c0-59f0-a4cf-4b4abe270388` | none |
| 5 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 6 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 7 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 8 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 9 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `9cc089f1-2aef-5cf3-a59c-485a5cc2d896` | none |
### parent
{"missing_evidence_ids": ["mitre_attack_v17_1-b7-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 5 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 6 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 7 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 8 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 10 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |

## rag_043 — hybrid

办公文档为什么能像小程序一样，在事件触发时自动执行主机任务？

Reference: VBA is event-driven and lets Office documents contain task-automation macros.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": ["security-v1-vba-event", "security-v1-vba-macros"], "first_relevant_rank": 8, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 3 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 4 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 5 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 6 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 7 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 8 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | security-v1-vba-event, security-v1-vba-macros |
| 9 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | none |
| 10 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 4, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 3 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 4 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | security-v1-vba-event, security-v1-vba-macros |
| 5 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 6 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 7 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 8 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 9 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 10 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |

## rag_049 — hybrid

数据库结果不直接出现在页面中时，测试者可以通过什么观察方式重建信息？

Reference: Inferential/blind injection sends requests and observes database behaviour.
Answerable: True; type=zh_to_en; language=zh->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `9cc089f1-2aef-5cf3-a59c-485a5cc2d896` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `6c66e942-1502-52ed-ab19-94214b0125d0` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `6953c28a-04dd-5a0d-a720-7a884e85255e` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `ca37ccd3-2bb8-531d-a521-0094c231c702` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `0c4540cf-878d-5a57-a41a-a0fc9a97b554` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `75753a76-01c0-59f0-a4cf-4b4abe270388` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `740e0686-93ed-5873-ab5e-55661a041917` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `a7198b85-a5f4-5b4f-86ac-a6a1db1a29eb` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f6ec1d6a-bc5a-5223-8988-b40d4f6e5a7c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 4, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `329dc788-b871-50b5-beb1-6fc94c41f58e` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | owasp_wstg_v4_2_sql_injection-b17-1 |
| 5 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `b2e6391b-7beb-5336-a631-dcad4a7ba57f` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |

## rag_066 — hybrid

Base64 或 URL encoding 在 Command Obfuscation 中起什么作用？

Reference: They are built-in forms of obfuscation that make command strings and patterns harder to signature and analyze.
Answerable: True; type=mixed_terms; language=mixed->en

### child
{"missing_evidence_ids": ["security-v1-obfuscation-purpose"], "recovered_below_cutoff": ["security-v1-obfuscation-purpose"], "first_relevant_rank": 1, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1027_010.md | `b4ad2cc2-f93b-5bce-98a6-be084e741260` | security-v1-obfuscation-encoding |
| 2 | attack_t1027_010.md | `3ff9fe68-110a-5623-b45d-5b6ddeb2ac79` | none |
| 3 | attack_t1027_010.md | `1a6dfdb7-1745-59ed-a476-c68e6e7e5283` | none |
| 4 | attack_t1027_010.md | `7242f3d0-ddae-53c5-925d-aac6db694099` | none |
| 5 | attack_t1027_010.md | `b76c5fc1-dc47-521d-b75c-a45527b3546c` | none |
| 6 | attack_t1027_010.md | `46d0cbdb-b125-5e29-acc1-c15ec8c0bc2c` | none |
| 7 | attack_t1027_010.md | `74e3d909-8b7d-5517-a2cf-a4491db86d5b` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `bf089b6c-ca1d-5fe1-a14d-11ea491056c1` | none |
| 9 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | security-v1-obfuscation-purpose |
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
| 6 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 9 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |

## rag_072 — hybrid

办公文件原本只是内容载体，哪种内置能力能让它在特定事件发生时自动执行主机任务？

Reference: VBA macros in Office documents can automate host tasks.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-vba-event", "security-v1-vba-macros"], "recovered_below_cutoff": ["security-v1-vba-event", "security-v1-vba-macros"], "first_relevant_rank": 6, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 3 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `5346b998-ec8f-5fc3-a273-44d80e07adbb` | none |
| 5 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 6 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | security-v1-vba-event, security-v1-vba-macros |
| 7 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 8 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 9 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 10 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | security-v1-vba-event, security-v1-vba-macros |
| 3 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 4 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 5 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 6 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 7 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 8 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 9 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 10 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |

## rag_074 — hybrid

不去猜用户的口令，而是寻找已经登录的会话留下的秘密，应查看哪里，又需要哪类身份才能提取？

Reference: Credential materials are stored in LSASS process memory and can be harvested by an administrative user or SYSTEM.
Answerable: True; type=paraphrase; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-lsass-memory", "security-v1-lsass-rights"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `4f1ddf29-046a-5279-b643-36ab6a0e0533` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `66f876e2-8cb6-5d98-81d0-2f756d6bf5ff` | none |
| 4 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `9358d189-d1e2-5f3f-a980-8cbf5c2f3086` | none |
| 6 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `f26f162c-7084-5cbf-adff-3870315cb474` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `de9a778a-4308-5260-9dd6-8226a6f05ef1` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b879b05a-7137-52f2-99e1-75521e9ea39b` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f6ec1d6a-bc5a-5223-8988-b40d4f6e5a7c` | none |
### parent
{"missing_evidence_ids": ["security-v1-lsass-memory", "security-v1-lsass-rights"], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": ["required_evidence_absent_from_saved_top_10", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 4 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 6 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `8f58fdb9-5926-566a-924d-e94cf16cf2ca` | none |

## rag_076 — hybrid

What account attack tries the same few common passwords across identities to avoid per-account lockout?

Reference: Password spraying.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | security-v1-spray-pattern, security-v1-spray-lockout |
| 2 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 3 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 4 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 5 | brute_force.md | `0caddcca-4cdf-5ae3-97d7-c39c4d5cd460` | none |
| 6 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 7 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 8 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 9 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `c60a5b0e-9732-5e3d-8ebd-d7da10dc5567` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | security-v1-spray-pattern, security-v1-spray-lockout |
| 2 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 3 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 4 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 5 | brute_force.md | `cb2c87f1-0241-5ad4-a053-5168b2cf5eef` | none |
| 6 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 7 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 8 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |

## rag_077 — hybrid

攻击者已经拿到外站泄露的成对账号密码，再利用用户复用习惯登录目标；这与轮试常见口令的模式如何区分？

Reference: Credential stuffing uses breach-dump credentials and password overlap.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 3, "hard_negative_ranks": [1], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | none |
| 2 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 3 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | security-v1-stuffing-reuse, security-v1-stuffing-cause |
| 4 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `9e442b7d-ac16-5d43-8fe3-a3bfb4317505` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `ea97e298-d534-5488-8103-036850028884` | none |
| 7 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | none |
| 8 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `c60a5b0e-9732-5e3d-8ebd-d7da10dc5567` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `d4ea4f63-f82a-5bc1-b774-0281046fbaa1` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 3, "hard_negative_ranks": [1], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 2 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 3 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | security-v1-stuffing-reuse, security-v1-stuffing-cause |
| 4 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 7 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |

## rag_078 — hybrid

Which technique uses a stolen hash to authenticate directly rather than cracking it back into a password?

Reference: Pass the Hash authenticates without the cleartext password.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [4], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | security-v1-pth-auth |
| 2 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ca37ccd3-2bb8-531d-a521-0094c231c702` | none |
| 4 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `4a868b13-59ee-51d9-8ec2-8f9151d99c8c` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `4f1ddf29-046a-5279-b643-36ab6a0e0533` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `9e442b7d-ac16-5d43-8fe3-a3bfb4317505` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `31462c85-b7d9-5376-8277-7c2fd302440c` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `0c4540cf-878d-5a57-a41a-a0fc9a97b554` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ea97e298-d534-5488-8103-036850028884` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [4], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | security-v1-pth-auth |
| 2 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 4 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 8 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 9 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b2e6391b-7beb-5336-a631-dcad4a7ba57f` | none |

## rag_079 — hybrid

分析目标是获取已登录会话留下的内存凭据，而不是使用现成摘要去认证；应该聚焦哪个安全进程？

Reference: LSASS process memory.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": ["security-v1-lsass-memory"], "first_relevant_rank": 8, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | sentence_continuation.pdf | `ef204da5-aaba-5b71-b07f-e8547de83589` | none |
| 3 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `75753a76-01c0-59f0-a4cf-4b4abe270388` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `5346b998-ec8f-5fc3-a273-44d80e07adbb` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `c60a5b0e-9732-5e3d-8ebd-d7da10dc5567` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `03c50ef4-caff-54c3-8a2b-64f25fca6bbe` | none |
| 8 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | security-v1-lsass-memory |
| 9 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `169a848c-8109-55ab-9ffb-e2b303a46899` | none |
### parent
{"missing_evidence_ids": ["security-v1-lsass-memory"], "recovered_below_cutoff": ["security-v1-lsass-memory"], "first_relevant_rank": 6, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff", "cross_language_mismatch_hypothesis_not_proven"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | sentence_continuation.pdf | `97baa698-acaf-5db6-a952-4175923e9637` | none |
| 3 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 6 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | security-v1-lsass-memory |
| 7 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `fe55b944-ceae-5f34-aef2-c13e8c1d03a9` | none |
| 9 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |

## rag_080 — hybrid

Which language mechanism best fits event-driven macros embedded in Office documents rather than webpage scripts?

Reference: Visual Basic for Applications (VBA) macros.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | security-v1-vba-event, security-v1-vba-macros |
| 2 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 3 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 4 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `75998bd9-0957-5c68-9b36-71f765b494a9` | none |
| 6 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `323f29d6-5027-5df8-92c9-64da1831f634` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f26f162c-7084-5cbf-adff-3870315cb474` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `5346b998-ec8f-5fc3-a273-44d80e07adbb` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `6953c28a-04dd-5a0d-a720-7a884e85255e` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | security-v1-vba-event, security-v1-vba-macros |
| 2 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 3 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 5 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 9 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `fc70da0c-00d2-524b-95ce-7a88039f1f71` | none |

## rag_081 — hybrid

线索明确是由系统脚本引擎解释的微软脚本实现，而非办公文档宏；应找哪个实现？

Reference: JScript.
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [3, 4], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 2 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | security-v1-js-engine |
| 3 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 4 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
| 5 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 6 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 7 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 8 | attack_t1027_010.md | `4c1af995-09cd-562a-be2e-dd98d0292492` | none |
| 9 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b34a5747-db9e-56c4-9bea-1f4a94076379` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 2, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 2 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | security-v1-js-engine |
| 3 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 4 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 5 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 6 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 7 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 8 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |

## rag_082 — hybrid

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
| 6 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `75998bd9-0957-5c68-9b36-71f765b494a9` | none |
| 8 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 9 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | none |
| 10 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | security-v1-batch |
| 2 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 3 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 4 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 6 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 7 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | none |
| 8 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 9 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 10 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |

## rag_083 — hybrid

需要远程修改注册表和服务，线索指向一种同名的系统服务与协议，而非仅仅本地命令解释器；它是什么？

Reference: Windows Remote Management (WinRM).
Answerable: True; type=technique_confusion; language=zh->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2, 3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | security-v1-winrm-service |
| 2 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 3 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 4 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 5 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 6 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 7 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `5346b998-ec8f-5fc3-a273-44d80e07adbb` | none |
| 9 | attack_t1027_010.md | `4c1af995-09cd-562a-be2e-dd98d0292492` | none |
| 10 | attack_t1027_010.md | `8b443a9a-15ef-5c89-9cd1-ad155513876c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2, 3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | security-v1-winrm-service |
| 2 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 3 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 4 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 5 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 6 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 8 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 9 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 10 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |

## rag_084 — hybrid

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
| 5 | attack_t1550_002.md | `8e4f8476-2f4d-54a6-a935-1cddda286fe2` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `75753a76-01c0-59f0-a4cf-4b4abe270388` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `03c50ef4-caff-54c3-8a2b-64f25fca6bbe` | none |
| 8 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `d4ea4f63-f82a-5bc1-b774-0281046fbaa1` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f6ec1d6a-bc5a-5223-8988-b40d4f6e5a7c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | security-v1-run-logon, security-v1-run-context |
| 2 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 3 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 4 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 5 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 7 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 9 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 10 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |

## rag_086 — hybrid

Which system scripting environment can download and execute programs in memory without touching disk, unlike batch-file or logon-entry mechanisms?

Reference: PowerShell.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [4], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | mitre_attack_v17_1-b7-1 |
| 2 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 3 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 4 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `75998bd9-0957-5c68-9b36-71f765b494a9` | none |
| 6 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 7 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `8f2bcaec-cf6c-563e-85ed-da0808c770a5` | none |
| 9 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 10 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [3], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | mitre_attack_v17_1-b7-1 |
| 2 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 3 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |
| 5 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 6 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 7 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 8 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 9 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 10 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |

## rag_088 — hybrid

Which retrieval method reconstructs information from database behaviour without receiving it through another channel?

Reference: Inferential/blind SQL injection.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": ["owasp_wstg_v4_2_sql_injection-b17-1"], "recovered_below_cutoff": ["owasp_wstg_v4_2_sql_injection-b17-1"], "first_relevant_rank": 6, "hard_negative_ranks": [], "reasons": ["relevant_evidence_ranked_below_cutoff"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `0c4540cf-878d-5a57-a41a-a0fc9a97b554` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `ca37ccd3-2bb8-531d-a521-0094c231c702` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `ea97e298-d534-5488-8103-036850028884` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `fa9dcae4-7c36-57dd-97b6-f2561547a545` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `4a868b13-59ee-51d9-8ec2-8f9151d99c8c` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `9e442b7d-ac16-5d43-8fe3-a3bfb4317505` | owasp_wstg_v4_2_sql_injection-b17-1 |
| 7 | owasp_wstg_v4_2_sql_injection.md | `4f1ddf29-046a-5279-b643-36ab6a0e0533` | none |
| 8 | mitre_attack_v17_1.md | `46cbe107-0b23-5a73-b111-47b7710432ad` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `f26f162c-7084-5cbf-adff-3870315cb474` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `f6ec1d6a-bc5a-5223-8988-b40d4f6e5a7c` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | owasp_wstg_v4_2_sql_injection-b17-1 |
| 2 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 4 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `be3a6543-c831-509c-b9ef-051451de7e81` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `7ac34c80-5cfb-591f-a7f3-edbbe2bd93cd` | none |
| 7 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `b2e6391b-7beb-5336-a631-dcad4a7ba57f` | none |

## rag_090 — hybrid

Which trusted Windows utility executes standalone HTA files rather than Office document macros?

Reference: Mshta.exe.
Answerable: True; type=technique_confusion; language=en->en

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2, 3, 5], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1218_005.md | `fa6c2f5e-6148-5af7-b0d2-ea447803511f` | security-v1-mshta-files, security-v1-mshta-outside |
| 2 | attack_t1059_005.md | `39d7bf82-4c36-5ba7-82d2-cbb8e32e257b` | none |
| 3 | attack_t1059_005.md | `e0d0dc54-f3b9-5cd9-9ee5-17015e54f481` | none |
| 4 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 5 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 6 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | none |
| 7 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 8 | attack_t1021_006.md | `2d7191a3-5a02-5160-8e52-245154ad5b4c` | none |
| 9 | mitre_attack_v17_1.md | `540ea747-41da-59ee-8cfc-15ec29520986` | none |
| 10 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": 1, "hard_negative_ranks": [2, 4], "reasons": ["known_similar_but_wrong_source_returned"], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1218_005.md | `2864d8d1-f727-578b-88f9-87d841924062` | security-v1-mshta-files, security-v1-mshta-outside |
| 2 | attack_t1059_005.md | `95883c1e-59f8-531d-aa8e-ac8e9d7808f7` | none |
| 3 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 4 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 5 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 6 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 7 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 8 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 9 | nist_sp80061r3_pp10-12.pdf | `51488a7b-8c0e-5155-8a98-ed8ea166729c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `45d84c94-be45-5847-b9d0-29499a927de4` | none |

## rag_091 — hybrid

我们租户当前到底连续失败几次才会锁定账号，锁定持续多少分钟？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 2 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 3 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | none |
| 4 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 5 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 6 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `b63df3a0-50c3-5f9a-8a7f-6c7bce42ca5b` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `07141a6b-0186-5015-9152-8e21752cf545` | none |
| 9 | mitre_attack_v17_1.md | `1ba1ee21-8635-5711-915e-773ef0e6ad7c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `ea97e298-d534-5488-8103-036850028884` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 2 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 3 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 4 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 5 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `2bacdf0d-4284-5d41-a0f4-6488d1895dbc` | none |
| 8 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |

## rag_092 — hybrid

这次内存采集实际提取到了哪些域用户的密码摘要？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `9358d189-d1e2-5f3f-a980-8cbf5c2f3086` | none |
| 3 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 4 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `5bbcdd61-fb5a-577d-8e3a-0e62e53635d3` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `b879b05a-7137-52f2-99e1-75521e9ea39b` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `be8f7de5-7e37-5b20-913a-cf48be6cc7d3` | none |
| 8 | attack_t1003_001.md | `1b52342b-7799-5baa-a127-ea516d9ab74c` | none |
| 9 | attack_t1110_004.md | `36853e34-7332-5f56-8ea0-e332da85f44d` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `07141a6b-0186-5015-9152-8e21752cf545` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |
| 3 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `f5027ad5-f7ff-5973-b491-5a21638e9b69` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 6 | attack_t1003_001.md | `0e5580ba-f3a3-5a3c-9306-e7d2bde9adf4` | none |
| 7 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `2bacdf0d-4284-5d41-a0f4-6488d1895dbc` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `383f9846-618e-5434-b2ce-18ef21755566` | none |
| 10 | mitre_attack_v17_1.md | `8d2245ff-cf7d-5822-8ae2-e4c407bd1b66` | none |

## rag_093 — hybrid

终端 SEC-WS-17 上的登录自启动条目是谁在什么时间写入的？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `aeb5baf8-08be-57b9-867f-621d6035494a` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `403e68c4-5e8f-516d-9032-8ff1464c8d19` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `de623621-9f23-5ec9-952e-b94cfe8184a4` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `88efa0e5-f4f4-5a67-bc9b-10552e7f174c` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `9e02014e-da89-5c22-93a7-51deb86c0217` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `ed8c99ae-daa8-51b3-b553-ab7ca4bd0f6f` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `ca5ac52b-4843-5283-8a9b-a0f1860d9076` | none |
| 9 | owasp_wstg_v4_2_sql_injection.md | `79524f44-ebec-56c2-b4e2-304c6472b929` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `de9a778a-4308-5260-9dd6-8226a6f05ef1` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `b22fc53a-ec4f-58ec-a9ad-40636cd713e7` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `8f58fdb9-5926-566a-924d-e94cf16cf2ca` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `ca445bf9-90ad-509b-b348-c19eaf3d2f5f` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `41ab0e15-b88b-5420-bb3d-a1f0c6b6ec99` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `4924a677-7a32-5c43-9fe3-8d16cd327837` | none |
| 7 | owasp_wstg_v4_2_sql_injection.md | `524cbd2f-44a7-5b8d-84c3-4f42fbe6e727` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `2bacdf0d-4284-5d41-a0f4-6488d1895dbc` | none |
| 9 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |
| 10 | owasp_wstg_v4_2_sql_injection.md | `9068b3d1-ded0-588b-9531-318eddad585d` | none |

## rag_094 — hybrid

昨晚触发编码脚本告警的外部来源地址具体是多少？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_007.md | `8081b163-afaf-5190-8226-c16ddc053d81` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `622eb9e0-4f0b-559b-94a4-968331834433` | none |
| 3 | owasp_wstg_v4_2_sql_injection.md | `67ab4d23-280e-5c55-9716-4810b8b000bb` | none |
| 4 | brute_force.md | `bdff355c-a9d0-524a-9d2f-5a595b19db8a` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `2c11415b-8b9d-5985-9a68-cb93d5e0b9b9` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `e9a4d66f-e907-5cd4-ab00-a72e238a1d9e` | none |
| 7 | attack_t1027_010.md | `4c1af995-09cd-562a-be2e-dd98d0292492` | none |
| 8 | nist_sp80061r3_pp10-12.pdf | `0054058a-7844-5b98-9ada-06310a90907e` | none |
| 9 | attack_t1547_001.md | `ba588ae9-482e-51dd-8605-e6b75b1337dc` | none |
| 10 | brute_force.md | `248d9fc6-316f-5292-a86c-63d04e9b9451` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | attack_t1059_007.md | `9d47d608-d805-5891-ad50-ad0f34344a0a` | none |
| 2 | owasp_wstg_v4_2_sql_injection.md | `b039ce3b-c3a2-51a3-837f-c12b693d3c7b` | none |
| 3 | brute_force.md | `9c6d5623-d9d1-5a7d-84da-c613a85cf282` | none |
| 4 | owasp_wstg_v4_2_sql_injection.md | `b2e6391b-7beb-5336-a631-dcad4a7ba57f` | none |
| 5 | owasp_wstg_v4_2_sql_injection.md | `4dfe19e5-443f-50fe-8091-64f2c49d9e2c` | none |
| 6 | attack_t1027_010.md | `31b05eda-ff77-5d2e-be4d-7e02398ce997` | none |
| 7 | nist_sp80061r3_pp10-12.pdf | `d0370bbf-b32f-576c-8801-c044fd0434f0` | none |
| 8 | attack_t1547_001.md | `f14b8453-0013-5cbd-9ded-aff710992602` | none |
| 9 | brute_force.md | `7ebc4ee3-1714-5c74-9e35-f5d19230bf88` | none |
| 10 | mitre_attack_v17_1.md | `f70e6204-af37-518f-be29-0cbd58e13320` | none |

## rag_095 — hybrid

本次主机隔离是否已经由值班人员实际执行成功？

Reference: Insufficient evidence: the corpus contains guidance, not the required tenant configuration, acquisition output, host audit log, alert record or action-execution result.
Answerable: False; type=unanswerable; language=zh->none

### child
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `5d5c299e-dc40-52e3-b592-38fe68895a1a` | none |
| 2 | attack_t1021_006.md | `47b8c8c2-0e92-5b69-9a3a-3d0a425725ae` | none |
| 3 | malware.md | `e09b2a00-f3d5-5eb6-bc06-82b042f21798` | none |
| 4 | attack_t1569_002.md | `6aa74254-fee3-5268-86fa-ee5667f9071b` | none |
| 5 | mitre_attack_v17_1.md | `f0f5770b-8bea-5b73-bb4b-ad730c26d616` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `655ef9c4-4eda-56b3-a435-d1d08c1e89b6` | none |
| 7 | attack_t1059_003.md | `6a29f214-e18d-5ae4-bf72-ecd05eb83a58` | none |
| 8 | owasp_wstg_v4_2_sql_injection.md | `07141a6b-0186-5015-9152-8e21752cf545` | none |
| 9 | mitre_attack_v17_1.md | `e016b4d5-29d9-5a36-be29-4f56084c78a0` | none |
| 10 | attack_t1110_003.md | `a86ab3a8-f027-57a3-bc09-c937479def13` | none |
### parent
{"missing_evidence_ids": [], "recovered_below_cutoff": [], "first_relevant_rank": null, "hard_negative_ranks": [], "reasons": [], "reason_scope": "Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison."}

| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |
| --- | --- | --- | --- |
| 1 | numbered_steps.docx | `315b6f9e-1f6c-5a30-b9c4-410f24edcccc` | none |
| 2 | attack_t1021_006.md | `b0bf46a1-c169-5a30-b7d1-a6ece3e0dc1e` | none |
| 3 | malware.md | `dba1b75f-5cf7-51a7-9393-5daee9064a55` | none |
| 4 | attack_t1569_002.md | `bf338212-9279-51d0-9db3-05b4f175f706` | none |
| 5 | mitre_attack_v17_1.md | `8b837f1c-14d7-5dcd-9edf-d3abf30be71e` | none |
| 6 | owasp_wstg_v4_2_sql_injection.md | `2bacdf0d-4284-5d41-a0f4-6488d1895dbc` | none |
| 7 | attack_t1059_003.md | `f0dbe279-2b81-52fa-90c0-c84611c53b5d` | none |
| 8 | attack_t1110_003.md | `07675d5f-341f-5969-b7f3-e3a64e13fe53` | none |
| 9 | attack_t1550_002.md | `3913ce83-0ca1-5e65-a251-6f343a80272c` | none |
| 10 | attack_t1110_004.md | `45577f31-35ac-500f-9a8b-264d449c4e74` | none |

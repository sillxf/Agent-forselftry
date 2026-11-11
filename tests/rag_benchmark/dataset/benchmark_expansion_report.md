# 现有 30 题覆盖审查与 100 题扩展报告

**AI 自动来源检查，不是人工审核通过。原 30 题和所有历史结果未覆盖。**

## 原 30 题统计

```json
{
  "questions": 30,
  "answerable": 25,
  "languages": {
    "en": 26,
    "mixed": 2,
    "zh": 2
  },
  "topics": {
    "account_abuse": 3,
    "authentication": 4,
    "credential_access": 1,
    "detection_rules": 3,
    "execution": 2,
    "incident_response": 6,
    "knowledge_gap": 5,
    "remote_execution": 1,
    "sql_injection": 5
  },
  "difficulty": {
    "easy": 8,
    "hard": 10,
    "medium": 12
  },
  "question_types": {
    "english": 15,
    "mixed_terms": 2,
    "paraphrase": 7,
    "unanswerable": 5,
    "zh_to_en": 1
  },
  "review_status": {
    "pending": 30
  },
  "named_reviewers": 0,
  "distinct_positive_sources": 9,
  "distinct_source_quote_facts": 39,
  "explicit_identifier_queries": [
    "rag_001",
    "rag_002",
    "rag_003",
    "rag_005",
    "rag_016"
  ],
  "mean_english_query_token_overlap_with_gold": 0.3005591630591631,
  "overlap_scope": "Non-stopword English query-token containment in positive quote text; this is a lexical proxy, not semantic hardness or a Chinese/English similarity metric.",
  "overlapping_multi_document_questions": []
}
```

## 原测试集缺陷

- 只有 9 份资料；ATT&CK 三个技术描述合在同一文件，缺少脚本/凭据技术之间的真实近邻干扰。
- 存在标题直接给答案、编号查表及原文术语显式出现的问题；保留为 sanity checks，不将其当困难语义任务。
- 词汇重合统计只是英文代理指标。中文旧题少，不能据其零英文词重合声称语义难度更高。
- 旧不可答题含 fictional 等明显提示；新增 5 个不带虚构提示、但缺实际配置/日志的近域知识缺口。
- 010 定义完整性、015 因果边界、024 逐项对应暗示、025 高权限描述仍需审查；原题不为提高分数改写。
- 现有 30 题全为 pending、reviewer 为空；未将 AI 核查改为人工通过。

## 扩展后的覆盖

```json
{
  "questions": 100,
  "answerable": 90,
  "languages": {
    "en": 40,
    "mixed": 15,
    "zh": 45
  },
  "topics": {
    "account_abuse": 6,
    "authentication": 15,
    "credential_access": 12,
    "detection_rules": 3,
    "execution": 25,
    "incident_response": 11,
    "knowledge_gap": 5,
    "persistence": 6,
    "remote_execution": 7,
    "sql_injection": 10
  },
  "difficulty": {
    "easy": 8,
    "hard": 51,
    "medium": 41
  },
  "question_types": {
    "english": 15,
    "mixed_terms": 15,
    "multi_document": 5,
    "paraphrase": 15,
    "technique_confusion": 15,
    "unanswerable": 10,
    "zh_to_en": 25
  },
  "review_status": {
    "pending": 100
  },
  "named_reviewers": 0,
  "distinct_positive_sources": 21,
  "distinct_source_quote_facts": 63,
  "explicit_identifier_queries": [
    "rag_001",
    "rag_002",
    "rag_003",
    "rag_005",
    "rag_016"
  ],
  "mean_english_query_token_overlap_with_gold": 0.28126310417977085,
  "overlap_scope": "Non-stopword English query-token containment in positive quote text; this is a lexical proxy, not semantic hardness or a Chinese/English similarity metric.",
  "overlapping_multi_document_questions": [
    "rag_096",
    "rag_097",
    "rag_098",
    "rag_099",
    "rag_100"
  ]
}
```

## 来源与证据

- 原 9 份文档逐字节复制；新增 12 份同一固定提交的 ATT&CK v17.1 官方描述节选。详见 v1/manifest.json。
- 新增问题设计、来源短引文、实际解析 Block ID 分别保存在 question_designs.json、evidence_designs.json、evidence_catalog.json。
- 全 100 题的证据引用已在真实索引校验：301 Child / 70 Parent。这是结构校验，不是人工语义批准。
- 10 个不可答题不包含正向 Evidence ID；相似检索结果不代表可回答。
- 5 个主要多文档题全部列出每个必要事实；其他分类与语言维度可能交叉，不把分组当成互斥统计。

## 设计修订与可比性

- 首版干扰题全部为中文，存在题型与语言混淆；按固定编号轮换把 14 道新增题改为语义等价的另一种提问语言。答案、证据、原 30 题不变。
- design_revisions.json 保留每项修改、前后哈希及原因；首轮与重复检查的原始实验仍封存。最终比较必须使用 r2 平衡语言版本，不能把它与首轮分数当成模型提升。

## 仍需注意

- All labels and literal English translations remain candidates pending review.
- Inherited 010/015/024/025 wording/support concerns are preserved, not silently repaired.
- Repeated facts across language variants are not independent examples; split future holdouts by fact family.
- No Agent or generation/refusal evaluation is performed by this retrieval benchmark.

此集是公开的开发候选集，不是独立留出集。没有根据本次分数回改问题、删除失败题或改变生产模型。

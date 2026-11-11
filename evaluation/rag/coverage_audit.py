"""Reproducible coverage/grounding audit and unsigned review sheets for Security V1."""
import argparse
import json
import re
from collections import Counter
from pathlib import Path
from statistics import mean

from evaluation.rag.dataset import Dataset, checksum, normalize
from evaluation.rag.expansion import LEGACY, V1, write

STOP=set('a an the is are to of in on for from by and or as with what which how why can does do be it its that when should using used without'.split())


def overlap(question):
    query=set(re.findall(r'[a-z][a-z0-9._-]*',question.question.lower()))-STOP
    source=set(re.findall(r'[a-z][a-z0-9._-]*',' '.join(e.text_quote for e in question.relevant_evidence).lower()))-STOP
    return len(query&source)/len(query) if query else None


def coverage(dataset):
    def counts(field): return dict(sorted(Counter(getattr(q,field) for q in dataset.questions).items()))
    values=[overlap(q) for q in dataset.questions if q.answerable and q.language=='en']
    values=[v for v in values if v is not None]
    return dict(questions=len(dataset.questions),answerable=sum(q.answerable for q in dataset.questions),
                languages=counts('language'),topics=counts('topic'),difficulty=counts('difficulty'),question_types=counts('question_type'),
                review_status=counts('review_status'),named_reviewers=sum(bool(q.reviewer) for q in dataset.questions),
                distinct_positive_sources=len({e.source for q in dataset.questions for e in q.relevant_evidence}),
                distinct_source_quote_facts=len({(e.document_id,normalize(e.text_quote)) for q in dataset.questions for e in q.relevant_evidence}),
                explicit_identifier_queries=[q.id for q in dataset.questions if re.search(r'\b(?:T\d{4}(?:\.\d{3})?|R\d{3}|WSTG-[A-Z]+-\d+)\b',q.question)],
                mean_english_query_token_overlap_with_gold=mean(values) if values else None,
                overlap_scope='Non-stopword English query-token containment in positive quote text; this is a lexical proxy, not semantic hardness or a Chinese/English similarity metric.',
                overlapping_multi_document_questions=[q.id for q in dataset.questions if len({e.document_id for e in q.relevant_evidence})>1])


def audit(storage):
    import os
    os.environ['HF_HUB_OFFLINE']='1';os.environ['TRANSFORMERS_OFFLINE']='1'
    from app.rag.retriever import KnowledgeRetriever
    legacy=Dataset(LEGACY/'dataset/questions.jsonl')
    legacy.validate_corpus()
    extended=Dataset(V1/'dataset/questions.jsonl')
    design=json.loads((V1/'question_designs.json').read_text(encoding='utf-8'))
    old_raw=[json.loads(l) for l in legacy.path.read_text(encoding='utf-8').splitlines()]
    new_raw=[json.loads(l) for l in extended.path.read_text(encoding='utf-8').splitlines()]
    for old,new in zip(old_raw,new_raw[:30]):
        assert all(new[key]==value for key,value in old.items()),old['id']
    assert checksum(legacy.path)==extended.metadata['legacy_dataset_sha256']
    for q in legacy.questions:
        for key,value in design['legacy_metadata'][q.id].items():
            setattr(q,key,value)
    extended.validate_corpus()
    retriever=KnowledgeRetriever(knowledge_dir=extended.documents_dir,storage_dir=storage)
    extended.validate_index(retriever)
    files={e['file'] for e in extended.manifest['documents']}
    for q in extended.questions:
        assert set(q.hard_negative_sources)<=files
        assert not set(q.hard_negative_sources)&{e.source for e in q.relevant_evidence}
    report=dict(audit_type='AI source/structure checks, not human approval',legacy_dataset_sha256=legacy.sha256,expanded_dataset_sha256=extended.sha256,
                legacy=coverage(legacy),expanded=coverage(extended),corpus_documents=len(files),
                inherited_core_fields_unchanged=True,all_100_evidence_locations_valid=True,
                prior_audit_inputs={name:checksum(LEGACY/'dataset'/name) for name in ['questions.jsonl','review.md','audit_notes.json','phase2_audit.md']},
                design_revision=json.loads((V1/'design_revisions.json').read_text(encoding='utf-8')) if (V1/'design_revisions.json').exists() else None,
                new_question_ids=[q.id for q in extended.questions[30:]],
                validation_index=dict(documents=len(retriever.documents),parents=len(retriever.parents),children=len(retriever.store.records)),
                limitations=['All labels and literal English translations remain candidates pending review.',
                             'Inherited 010/015/024/025 wording/support concerns are preserved, not silently repaired.',
                             'Repeated facts across language variants are not independent examples; split future holdouts by fact family.',
                             'No Agent or generation/refusal evaluation is performed by this retrieval benchmark.'])
    write(V1/'dataset/coverage.json',report)
    lines=['# 现有 30 题覆盖审查与 100 题扩展报告','',
           '**AI 自动来源检查，不是人工审核通过。原 30 题和所有历史结果未覆盖。**','',
           '## 原 30 题统计','', '```json',json.dumps(report['legacy'],ensure_ascii=False,indent=2),'```','',
           '## 原测试集缺陷','',
           '- 只有 9 份资料；ATT&CK 三个技术描述合在同一文件，缺少脚本/凭据技术之间的真实近邻干扰。',
           '- 存在标题直接给答案、编号查表及原文术语显式出现的问题；保留为 sanity checks，不将其当困难语义任务。',
           '- 词汇重合统计只是英文代理指标。中文旧题少，不能据其零英文词重合声称语义难度更高。',
           '- 旧不可答题含 fictional 等明显提示；新增 5 个不带虚构提示、但缺实际配置/日志的近域知识缺口。',
           '- 010 定义完整性、015 因果边界、024 逐项对应暗示、025 高权限描述仍需审查；原题不为提高分数改写。',
           '- 现有 30 题全为 pending、reviewer 为空；未将 AI 核查改为人工通过。', '',
           '## 扩展后的覆盖','', '```json',json.dumps(report['expanded'],ensure_ascii=False,indent=2),'```','',
           '## 来源与证据','',
           '- 原 9 份文档逐字节复制；新增 12 份同一固定提交的 ATT&CK v17.1 官方描述节选。详见 v1/manifest.json。',
           '- 新增问题设计、来源短引文、实际解析 Block ID 分别保存在 question_designs.json、evidence_designs.json、evidence_catalog.json。',
           f"- 全 100 题的证据引用已在真实索引校验：{len(retriever.store.records)} Child / {len(retriever.parents)} Parent。这是结构校验，不是人工语义批准。",
           '- 10 个不可答题不包含正向 Evidence ID；相似检索结果不代表可回答。',
           '- 5 个主要多文档题全部列出每个必要事实；其他分类与语言维度可能交叉，不把分组当成互斥统计。', '',
           '## 设计修订与可比性','',
           '- 首版干扰题全部为中文，存在题型与语言混淆；按固定编号轮换把 14 道新增题改为语义等价的另一种提问语言。答案、证据、原 30 题不变。',
           '- design_revisions.json 保留每项修改、前后哈希及原因；首轮与重复检查的原始实验仍封存。最终比较必须使用 r2 平衡语言版本，不能把它与首轮分数当成模型提升。','',
           '## 仍需注意','',*['- '+x for x in report['limitations']], '',
           '此集是公开的开发候选集，不是独立留出集。没有根据本次分数回改问题、删除失败题或改变生产模型。']
    (LEGACY/'dataset/benchmark_expansion_report.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')
    sheet=['# Security V1 Ground Truth 审核清单','',
           '全部状态来自 JSONL；AI 校验不能勾选人工通过。id 对应 question_id；relevant_evidence[].evidence_id 对应 evidence_ids。','',
           '- [ ] 问题可由引用完整回答，不依赖标题猜测、未给出的日志或因果推断。',
           '- [ ] 核对全部必要事实、等价替代位置和多文档依赖。',
           '- [ ] 核对自然中文/术语/英文翻译是否语义一致，没有漏条件或添加答案。',
           '- [ ] 确认干扰来源确实相似但不能满足本问题要求。',
           '- [ ] 知识缺口题已确认在整套冻结资料中不存在答案。','']
    translations = json.loads((V1/'english_queries.json').read_text(encoding='utf-8'))
    for q in extended.questions:
        translation = translations[q.id]
        sheet += [f'## {q.id} — {q.question_type}', '', q.question,'',f'参考答案：{q.expected_answer}',
                  f'语言：{q.language} → {q.document_language}；主题：{q.topic}；难度：{q.difficulty}',
                  f'状态：{q.review_status}；审核人：{q.reviewer or "未填写"}',f'设计说明：{q.design_note}',f'查询族：{q.query_family}',
                  f'对照实验英文 Query：{translation["english"]}',
                  f'翻译审核状态：{translation["review_status"]}；审核人：{translation["reviewer"] or "未填写"}',
                  '干扰来源：'+(', '.join(q.hard_negative_sources) or '未指定专用干扰源；仍检索完整语料'),'']
        for e in q.relevant_evidence:
            sheet += [f'- `{e.evidence_id}` — {e.source}；章节 {" > ".join(e.section_path)}；页 {e.page_number}–{e.page_end}',
                      f'  - 原文：{e.text_quote}',f'  - Block IDs：{", ".join(e.source_block_ids)}；同义位置 {len(e.alternatives)} 个']
            for alternative in e.alternatives:
                sheet += [f'  - 等价替代：{alternative.source}；章节 {" > ".join(alternative.section_path)}；页 {alternative.page_number}–{alternative.page_end}',
                          f'    - 原文：{alternative.text_quote}',
                          f'    - Block IDs：{", ".join(alternative.source_block_ids)}']
        if not q.answerable: sheet += ['- 无正向证据；不得将邻近指导文档标作本事件事实。']
        sheet += ['- [ ] 核对问题/答案/全部证据/翻译后，真实审核人再更新 JSONL；默认不批准。','']
    (V1/'dataset/review.md').write_text('\n'.join(sheet)+'\n',encoding='utf-8')
    (LEGACY/'dataset/benchmark_review_checklist.md').write_text('# 扩展版审核入口\n\n逐题问题、答案、原始引文、真实 Block ID、设计说明、干扰来源及未勾选的审核项见\n[100 题 Ground Truth 清单](../v1/dataset/review.md)。\n\n现有 30 题保留原有状态；新增 70 题和 100 条实验翻译均待审核。AI 来源定位校验不构成人工批准。\n',encoding='utf-8')
    print('Audited legacy and expanded dataset; generated unsigned checklist.')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--storage-dir',type=Path,default=Path(__file__).resolve().parents[2]/'app/storage/security-v1-minilm')
    args=parser.parse_args()
    audit(args.storage_dir)


if __name__=='__main__': main()

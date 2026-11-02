"""Focused checks for immutable legacy labels, grounded V1 data and query routing."""
import json
from collections import Counter
from pathlib import Path
from unittest.mock import Mock
from types import SimpleNamespace

from app.rag.retrieval.fusion import RRFFusion
from evaluation.rag.dataset import Dataset
from evaluation.rag.model_comparison import load_reference, dual_query_rank

ROOT=Path(__file__).resolve().parents[1]
V1=ROOT/'tests/rag_benchmark/v1'
BASE=ROOT/'evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm'


def test_v1_keeps_all_legacy_fields_and_real_review_statuses():
    old=[json.loads(l) for l in (ROOT/'tests/rag_benchmark/dataset/questions.jsonl').read_text(encoding='utf-8').splitlines()]
    rows=[json.loads(l) for l in (V1/'dataset/questions.jsonl').read_text(encoding='utf-8').splitlines()]
    assert len(rows)==100 and len({q['id'] for q in rows})==100 and len({q['question'] for q in rows})==100
    for before,after in zip(old,rows[:30]):
        assert all(after[k]==v for k,v in before.items())
    from evaluation.rag.expansion import compose_questions
    design=json.loads((V1/'question_designs.json').read_text(encoding='utf-8'))
    catalog=json.loads((V1/'evidence_catalog.json').read_text(encoding='utf-8'))
    assert compose_questions(old,design,catalog)==rows
    assert all(q['review_status']=='pending' and q['reviewer'] is None for q in rows)
    assert Counter(q['question_type'] for q in rows)==dict(english=15,zh_to_en=25,mixed_terms=15,paraphrase=15,technique_confusion=15,unanswerable=10,multi_document=5)
    for category in ['paraphrase','technique_confusion','multi_document']:
        assert {q['language'] for q in rows if q['question_type']==category}>={'en','zh'}
    for q in rows:
        assert bool(q['relevant_evidence'])==q['answerable']
        if q['question_type']=='multi_document':
            assert len({e['document_id'] for e in q['relevant_evidence']})>=2
    translations=json.loads((V1/'english_queries.json').read_text(encoding='utf-8'))
    assert set(translations)=={q['id'] for q in rows}
    assert all(translations[q['id']]['original']==q['question'] and translations[q['id']]['review_status']=='pending' for q in rows)


def test_all_v1_evidence_resolves_against_the_real_frozen_index():
    dataset=Dataset(V1/'dataset/questions.jsonl')
    dataset.validate_corpus()
    config=json.loads((BASE/'hybrid/config.json').read_text(encoding='utf-8'))
    assert dataset.sha256==config['dataset']['sha256']
    retriever=load_reference(dataset,BASE,config)
    dataset.validate_index(retriever)
    assert len(retriever.documents)==21


def test_dual_query_has_two_dense_routes_and_only_english_bm25():
    record=dict(chunk_id='chunk',block_ids=['block'],dense_score=.5)
    pipeline=SimpleNamespace(bm25_top_k=20,rank_candidates=Mock(return_value=[record]),
                             sparse=SimpleNamespace(retrieve=Mock(return_value=[dict(record,sparse_score=1)])),
                             fusion=RRFFusion(),context_builder=SimpleNamespace(build=Mock(return_value=[])))
    retriever=SimpleNamespace(pipeline=pipeline)
    result=dual_query_rank(retriever,'中文提问','English query',10)
    assert [c.args for c in pipeline.rank_candidates.call_args_list]==[('中文提问',10,'dense'),('English query',10,'dense')]
    pipeline.sparse.retrieve.assert_called_once_with('English query',40)
    assert [r['kind'] for r in result['query_routes']]==['dense','dense','bm25']
    pipeline.rank_candidates.reset_mock()
    dual_query_rank(retriever,'English query','English query',10)
    pipeline.rank_candidates.assert_called_once_with('English query',10,'dense')
    fused=RRFFusion().fuse([[record,record],[record]])
    assert len(fused)==1 and fused[0]['score']==2/61

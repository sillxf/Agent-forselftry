"""Focused checks for rank semantics, source mapping and the real retrieval adapter."""
import json
from math import log2
from pathlib import Path
from unittest.mock import Mock

import pytest

from app.rag.evaluation.dataset import Dataset, Evidence, SourceAnchor
from app.rag.evaluation.report import build_report
from app.rag.evaluation.retrieval_metrics import retrieval_metrics
from app.rag.evaluation.runner import derive_qrels, ranking_diagnostics, map_evidence, portable_record, ranking_fingerprint, run_benchmark


@pytest.mark.parametrize("ranks,grades,ideal,k,recall,precision,mrr", [
    ([["a"], ["b"]], {"a": 3, "b": 2}, [3, 2], 2, 1, 1, 1),
    ([[], ["a"], ["a"], ["b"]], {"a": 3, "b": 2}, [3, 3, 2], 3, .5, 2/3, .5),
    ([], {"a": 3}, [3], 5, 0, 0, 0),
    ([["a"]], {"a": 3}, [3], 5, 1, .2, 1),
    ([["a", "b"]], {"a": 3, "b": 2}, [3], 2, 1, .5, 1),
    ([["not_relevant"]], {"not_relevant": 0, "a": 1}, [1], 1, 0, 0, 0),
])
def test_metrics_preserve_result_slots_and_distinguish_facts_from_results(ranks, grades, ideal, k, recall, precision, mrr):
    metrics = retrieval_metrics(ranks, grades, k, ideal_result_grades=ideal)
    assert metrics["recall"] == recall
    assert metrics["precision"] == precision
    assert metrics["mrr"] == mrr
    assert 0 <= metrics["ndcg"] <= 1


def test_ndcg_uses_the_same_result_unit_in_dcg_and_idcg():
    grades = {"a": 3, "b": 1}
    expected = (1 + 1 / log2(3) + 7 / log2(4)) / (7 + 1 / log2(3) + 1 / log2(4))
    assert retrieval_metrics([["b"], ["b"], ["a"]], grades, 3,
                             ideal_result_grades=[3, 1, 1])["ndcg"] == pytest.approx(expected)
    # A single perfectly ranked result can contain several complete evidence facts.
    assert retrieval_metrics([["a", "b"]], grades, 5, ideal_result_grades=[3])["ndcg"] == 1
    # The high-grade result outside Top K must still contribute to the ideal ranking.
    assert retrieval_metrics([["b"]], grades, 1, ideal_result_grades=[3, 1])["ndcg"] == pytest.approx(1/7)
    assert retrieval_metrics([], {}, 5, ideal_result_grades=[]) == dict(recall=None, precision=None, mrr=None, ndcg=None)
    with pytest.raises(ValueError):
        retrieval_metrics([], {}, 0, ideal_result_grades=[])


def test_mapping_requires_document_identity_block_and_actual_text():
    evidence = Evidence(evidence_id="rule-r004", document_id="document", source="rules.pdf",
                        source_block_ids=["table"], section_path=[], text_quote="Rule ID: R004", relevance_grade=3)
    result = dict(document_id="document", source_block_ids=["table"], content="Rule ID: R001")
    assert map_evidence(result, [evidence]) == []  # same table, wrong row
    result["content"] = "Rule ID: R004"
    assert map_evidence(result, [evidence]) == ["rule-r004"]
    assert map_evidence(dict(result, document_id="other"), [evidence]) == []
    assert map_evidence(dict(result, source_block_ids=["other"]), [evidence]) == []


def test_alternative_anchors_credit_one_fact_not_two_requirements():
    evidence = Evidence(evidence_id="collect-logs", document_id="document", source="steps.docx",
                        source_block_ids=["english"], section_path=[], text_quote="Collect logs", relevance_grade=3,
                        alternatives=[SourceAnchor(document_id="document", source="steps.docx",
                            source_block_ids=["chinese"], section_path=[], text_quote="收集日志")])
    result = dict(document_id="document", source_block_ids=["chinese"], content="收集日志")
    assert map_evidence(result, [evidence]) == ["collect-logs"]
    metrics = retrieval_metrics([map_evidence(result, [evidence])], {"collect-logs": 3}, 1,
                                ideal_result_grades=[3, 3])
    assert metrics == dict(recall=1, precision=1, mrr=1, ndcg=1)


def test_checked_in_dataset_and_corpus_are_consistent_and_review_status_is_enforced():
    dataset = Dataset(Path(__file__).parent / "rag_benchmark/dataset/questions.jsonl")
    dataset.validate_corpus()
    assert len(dataset.questions) == 30
    assert sum(q.answerable for q in dataset.questions) == 25
    assert len({q.category for q in dataset.questions}) == 6
    assert dataset.pending_count == sum(q.review_status != "approved" for q in dataset.questions)
    if dataset.pending_count:
        with pytest.raises(ValueError, match="human review"):
            Dataset(dataset.path, require_reviewed=True)


def make_dataset(tmp_path, retriever):
    root = tmp_path / "benchmark"
    root.mkdir()
    data = root / "dataset"
    data.mkdir()
    document = retriever.documents[0]
    parent = next(iter(retriever.parents.values()))
    block = next(b for b in parent.blocks if "failed login" in b.text)
    question = dict(id="q1", question="failed login", category="semantic", difficulty="easy", answerable=True,
        expected_answer="Investigate failed logins", rationale="Source paragraph contains the detection evidence.",
        relevant_evidence=[dict(evidence_id="logins", document_id=document.document_id, source=document.filename,
            source_block_ids=block.source_block_ids or [block.block_id], section_path=block.section_path,
            page_number=block.page_number, page_end=block.page_end, text_quote="failed login", relevance_grade=3)])
    unknown = dict(question, id="q2", question="unavailable appliance password", answerable=False,
                   relevant_evidence=[], expected_answer="Insufficient knowledge", rationale="No appliance credentials are included.")
    (data / "questions.jsonl").write_text("\n".join(json.dumps(q) for q in [question, unknown]), encoding="utf-8")
    (data / "dataset.json").write_text(json.dumps(dict(schema_version=1, version="test", documents_dir=str(retriever.knowledge_dir))), encoding="utf-8")
    manifest = retriever.knowledge_dir.parent / "manifest.json"
    manifest.write_text(json.dumps(dict(version="test", documents=[dict(file=document.filename, sha256=document.checksum)])), encoding="utf-8")
    return Dataset(data / "questions.jsonl")


def test_runner_reuses_actual_retriever_separates_parent_and_keeps_unknown_results(rag_factory, tmp_path):
    (rag_factory.knowledge / "manual.md").write_text("# Detection\n\nRepeated failed login attempts require investigation.", encoding="utf-8")
    retriever = rag_factory()
    dataset = make_dataset(tmp_path, retriever)
    original = retriever.search_rankings
    retriever.search_rankings = Mock(wraps=original)
    rows = run_benchmark(dataset, retriever, top_k=5)
    assert rows[0]["child_metrics"]["recall"] == rows[0]["parent_metrics"]["recall"] == 1
    assert rows[0]["derived_qrels"]["children"] and rows[0]["derived_qrels"]["parents"]
    assert rows[0]["child_metrics"]["ndcg"] == 1
    assert rows[1]["children"] and rows[1]["child_metrics"]["recall"] is None
    unknown = rows[1]["diagnostics"]["unanswerable_assessment"]
    assert unknown["returned_neighbour_context"] is True
    assert unknown["knowledge_gap_detection"] == "not_evaluated"
    assert unknown["incorrect_answer_or_refusal"] == "not_evaluated_retrieval_only"
    assert [call.args[0] for call in retriever.search_rankings.call_args_list] == [q.question for q in dataset.questions]
    assert original("failed login", 2)["parents"] == retriever.search("failed login", 2)
    assert original("", 2) == dict(children=[], parents=[], candidate_count=0)
    retriever.embedding_fn = Mock(side_effect=AssertionError("BM25 must not embed a query"))
    assert original("failed login", 2, "bm25")["children"]
    with pytest.raises(ValueError, match="strategy"):
        original("failed login", 2, "invalid")

    output = tmp_path / "reports"
    output.mkdir()
    config = dict(retrieval=dict(top_k=5,strategy="hybrid"), annotation_status="provisional",
                  dataset=dict(version="test",sha256=dataset.sha256), code=dict(commit="test",dirty=True,source_sha256="test"))
    metrics = build_report(output, config, rows)
    assert metrics["overall"]["answerable"] == 1
    assert metrics["overall"]["unanswerable_stats"]["returned_context_count"] == 1
    assert metrics["overall"]["unanswerable_stats"]["correct_refusal_rate"] is None
    assert "provisional" in (output / "report.md").read_text(encoding="utf-8")
    import copy
    assert portable_record({"image_paths": ["D:/old-location/doc-hash/image.png"]}) == portable_record(
        {"image_paths": ["X:/new-location/doc-hash/image.png"]})
    assert ranking_fingerprint(rows) == ranking_fingerprint([dict(r, latency_ms=99) for r in rows])
    changed = copy.deepcopy(rows)
    changed[0]["children"][0]["rank"] = 2
    assert ranking_fingerprint(rows) != ranking_fingerprint(changed)
    retriever.search_rankings = Mock(side_effect=RuntimeError("test query failure"))
    failed = run_benchmark(dataset, retriever, top_k=5)
    assert failed[0]["child_metrics"]["recall"] == 0
    assert failed[0]["failure_types"] == ["retrieval_error"]

    evidence = dataset.questions[0].relevant_evidence[0]
    evidence.alternatives = [SourceAnchor(**evidence.model_dump(exclude={"evidence_id", "relevance_grade", "alternatives"}))]
    evidence.alternatives[0].source_block_ids = ["stale-alternative"]
    with pytest.raises(ValueError, match="Unresolved"):
        dataset.validate_index(retriever)
    evidence.alternatives = []
    dataset.questions[0].relevant_evidence[0].source_block_ids = ["stale-block"]
    with pytest.raises(ValueError, match="Unresolved"):
        dataset.validate_index(retriever)
    (rag_factory.knowledge / "manual.md").write_text("Changed corpus", encoding="utf-8")
    with pytest.raises(ValueError, match="manifest"):
        dataset.validate_corpus()


@pytest.mark.parametrize("change", ["duplicate_id", "invalid_grade", "unknown_without_rationale", "approved_without_reviewer"])
def test_dataset_rejects_broken_annotations(tmp_path, change):
    original = Dataset(Path(__file__).parent / "rag_benchmark/dataset/questions.jsonl")
    records = [q.model_dump() for q in original.questions]
    if change == "duplicate_id":
        records[1]["id"] = records[0]["id"]
    elif change == "invalid_grade":
        records[0]["relevant_evidence"][0]["relevance_grade"] = 4
    elif change == "unknown_without_rationale":
        records[-1]["rationale"] = ""
    else:
        records[0]["review_status"] = "approved"
        records[0]["reviewer"] = None
    (tmp_path / "dataset.json").write_text(json.dumps(original.metadata), encoding="utf-8")
    (tmp_path / "questions.jsonl").write_text("\n".join(json.dumps(q) for q in records), encoding="utf-8")
    with pytest.raises(ValueError):
        Dataset(tmp_path / "questions.jsonl")


def test_multiple_alternatives_and_parent_units_do_not_multiply_facts():
    from app.rag.evaluation.dataset import Question
    a = Evidence(evidence_id="a", document_id="d", source="test.md", source_block_ids=["a1"],
                 section_path=[], text_quote="first", relevance_grade=3,
                 alternatives=[SourceAnchor(document_id="d", source="test.md", source_block_ids=[key],
                     section_path=[], text_quote=quote) for key, quote in [("a2", "第一"), ("a3", "premier")]])
    b = Evidence(evidence_id="b", document_id="d", source="test.md", source_block_ids=["b"],
                 section_path=[], text_quote="second", relevance_grade=2)
    q = Question(id="q", question="two facts?", category="test", difficulty="easy", answerable=True,
                 expected_answer="first and second", relevant_evidence=[a, b], rationale="two independent facts")
    children = [dict(chunk_id=key, document_id="d", source_block_ids=[key], content=text)
                for key, text in [("a1", "first"), ("a2", "第一"), ("b", "second")]]
    parents = [dict(parent_id="p", document_id="d", source_block_ids=["a1", "b"], content="first second")]
    qrels = derive_qrels(q, {"children": children, "parents": parents})
    assert qrels == {"children": {"a1": 3, "a2": 3, "b": 2}, "parents": {"p": 3}}
    child_matches = [map_evidence(r, q.relevant_evidence) for r in children]
    parent_matches = [map_evidence(r, q.relevant_evidence) for r in parents]
    for k, expected_recall in [(1, .5), (2, .5), (3, 1)]:
        child = retrieval_metrics(child_matches, {"a": 3, "b": 2}, k, ideal_result_grades=list(qrels["children"].values()))
        parent = retrieval_metrics(parent_matches, {"a": 3, "b": 2}, k, ideal_result_grades=list(qrels["parents"].values()))
        assert child["recall"] == expected_recall
        assert parent["recall"] == parent["ndcg"] == 1
        assert child["ndcg"] == 1
        assert parent["precision"] == 1 / k
    cr = [dict(r, rank=i, matched_evidence=child_matches[i-1]) for i, r in enumerate(children[:2], 1)]
    pr = [dict(parents[0], rank=1, matched_evidence=["a", "b"])]
    diagnostic = ranking_diagnostics(q, cr, pr, qrels)
    assert diagnostic["parent_only_facts"] == ["b"]
    assert diagnostic["positive_children_outside_top_k"] == ["b"]
    assert ranking_diagnostics(q, cr, [], qrels)["child_only_facts"] == ["a"]


def test_dataset_rejects_shared_id_for_different_table_rules(tmp_path):
    source = Path(__file__).parent / "rag_benchmark/dataset"
    records = [json.loads(line) for line in (source / "questions.jsonl").read_text(encoding="utf8").splitlines()]
    rules = [q for q in records if q["id"] in {"rag_005", "rag_016", "rag_017"}]
    assert {q["relevant_evidence"][0]["evidence_id"] for q in rules} == {
        "continued_rules-r002", "continued_rules-r003", "continued_rules-r004"}
    for q in rules:
        q["relevant_evidence"][0]["evidence_id"] = "same-table-not-same-fact"
    (tmp_path / "dataset.json").write_bytes((source / "dataset.json").read_bytes())
    (tmp_path / "questions.jsonl").write_text("\n".join(json.dumps(q) for q in records), encoding="utf8")
    with pytest.raises(ValueError, match="different facts"):
        Dataset(tmp_path / "questions.jsonl")

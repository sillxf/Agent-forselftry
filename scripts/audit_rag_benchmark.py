"""Audit source labels and ranking failures without granting human review or tuning retrieval."""
import argparse
import json
import sys
from statistics import mean
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.rag.evaluation.dataset import Dataset, Evidence, checksum
from app.rag.evaluation.runner import derive_qrels, evaluation_units, map_evidence, portable_record, write_json
from app.rag.retriever import KnowledgeRetriever, tokenize
from app.rag.evaluation.retrieval_metrics import retrieval_metrics


CONTROL_QUERIES = {
    "rag_011": "What actions does the local brute-force alert response checklist recommend?",
    "rag_014": "What prevention measures are listed in the local SQL injection knowledge base?",
}


def render_review(dataset, notes):
    lines = ["# 30 题来源审查与人工复核单", "",
             "**来源核对由 AI 完成，不等于人工相关性批准。所有待审核状态保持不变。**", "",
             f"数据集：`{dataset.metadata['version']}`。JSONL 是标签的唯一事实来源。",
             "一个 evidence_id 表示一项事实；alternatives 是相同事实的 OR 位置，不增加 Recall 分母。",
             "确认问题、答案、所有有效来源、分级、实际页码/章节后，由真实审核人填写 reviewer 并批准。", ""]
    for question in dataset.questions:
        note = notes[question.id]
        lines += [f"## {question.id} — {question.category}", "", question.question, "",
                  f"参考答案：{question.expected_answer}", f"依据：{question.rationale}",
                  f"来源审查：{note['source_audit_note']}",
                  f"人工状态：`{question.review_status}`；审核人：`{question.reviewer}`", ""]
        if note.get("phase2_fact_review"):
            lines += [f"本轮事实检查：{note['phase2_fact_review']}",
                      f"所需证据范围：`{note['requested_evidence_scope']}`", ""]
        for evidence in question.relevant_evidence:
            lines += [f"### 事实 `{evidence.evidence_id}`（grade={evidence.relevance_grade}）", ""]
            for index, anchor in enumerate(evidence.anchors()):
                label = "主位置" if index == 0 else "同义替代位置（OR）"
                lines += [f"- {label}：`{anchor.source}`；索引页范围：{anchor.page_number}–{anchor.page_end}",
                          f"  - Document ID：`{anchor.document_id}`",
                          f"  - 原始 Block：{', '.join('`' + key + '`' for key in anchor.source_block_ids)}",
                          f"  - 解析章节：{' > '.join(anchor.section_path) or '(none)'}",
                          f"  - 原文：{anchor.text_quote.replace(chr(10), ' / ')}", ""]
        if "visible_source_section" in note:
            lines += [f"源文档可见章节：{' > '.join(note['visible_source_section'])}",
                      "注意：解析章节可能错误；此字段是来源核对，不冒充当前索引已修复。", ""]
        for decision in note["human_decisions"]:
            lines.append(f"- [ ] 人工确认：{decision}")
        lines += ["- [ ] 确认其他同义证据没有漏标，参考答案完整且没有混用当前事件事实。", ""]
    (dataset.path.parent / "review.md").write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "tests/rag_benchmark/dataset/questions.jsonl")
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--previous", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-01_candidate")
    parser.add_argument("--storage-dir", type=Path, default=ROOT / "app/storage/benchmark")
    args = parser.parse_args()
    config = json.loads((args.baseline / "hybrid/config.json").read_text(encoding="utf-8"))
    if config["retrieval"]["top_k"] != 5:
        raise ValueError("This source audit compares the fixed K=5 historical baseline")
    dataset = Dataset(args.dataset)
    dataset.validate_corpus()
    if config["dataset"]["sha256"] != dataset.sha256:
        raise ValueError("Audit dataset must match the saved experiment annotations")
    retriever = KnowledgeRetriever(knowledge_dir=dataset.documents_dir, storage_dir=args.storage_dir)
    dataset.validate_index(retriever)
    units = evaluation_units(retriever)
    notes_path = dataset.path.parent / "audit_notes.json"
    notes = json.loads(notes_path.read_text(encoding="utf-8"))["questions"]
    render_review(dataset, notes)
    source_checks, diagnostics = [], []
    for question in dataset.questions:
        anchors = []
        for evidence in question.relevant_evidence:
            for number, anchor in enumerate(evidence.anchors()):
                anchor_evidence = evidence.model_copy(update={**anchor.model_dump(), "alternatives": []})
                matching = [c["chunk_id"] for c in units["children"] if map_evidence(c, [anchor_evidence])]
                anchors.append({"evidence_id": evidence.evidence_id, "alternative_number": number,
                                **anchor.model_dump(), "quote_characters": len(anchor.text_quote),
                                "matching_child_ids": matching})
        qrels = derive_qrels(question, units)
        found = {eid for unit in units["children"] for eid in map_evidence(unit, question.relevant_evidence)}
        required = {e.evidence_id for e in question.relevant_evidence if e.relevance_grade > 0}
        source_checks.append({"question_id": question.id, "source_locations_valid": True,
                              "human_review_status": question.review_status, "anchors": anchors,
                              "unreachable_positive_facts": sorted(required - found),
                              "positive_child_units": len(qrels["children"]), "positive_parent_units": len(qrels["parents"]),
                              "notes": notes[question.id]})
        if question.id not in {"rag_002", "rag_003", "rag_004", "rag_011", "rag_014", "rag_016", "rag_018"}:
            continue
        variants = {"original": question.question}
        if question.id in CONTROL_QUERIES:
            variants["english_diagnostic_only"] = CONTROL_QUERIES[question.id]
        for variant, query in variants.items():
            for strategy in ("dense", "bm25", "hybrid"):
                ranked = retriever._rank_children(query, 5, strategy)
                items, first_match = [], None
                for rank, record in enumerate(ranked, 1):
                    source = dict(record, source_block_ids=record["block_ids"])
                    matches = map_evidence(source, question.relevant_evidence)
                    if matches and first_match is None:
                        first_match = rank
                    items.append({"rank": rank, "chunk_id": record["chunk_id"], "source": record["source_name"],
                                  "section_path": record["section_path"], "content": record["content"],
                                  "matched_evidence": matches, "query_term_overlap": sorted(set(tokenize(query)) & set(tokenize(record["search_text"]))),
                                  "dense_score": record.get("dense_score"), "sparse_score": record.get("sparse_score"),
                                  "rrf_score": record.get("score")})
                diagnostics.append({"question_id": question.id, "variant": variant, "query": query,
                                    "included_in_benchmark_averages": variant == "original",
                                    "strategy": strategy, "query_terms": tokenize(query),
                                    "candidate_count": len(ranked), "first_positive_candidate_rank": first_match,
                                    "top5": items[:5], "positive_candidate_rows": [item for item in items if item["matched_evidence"]]})
    comparisons, reconciliation = {}, {}
    for strategy in ("dense", "bm25", "hybrid"):
        old_path = args.previous / strategy / "retrieval_results.jsonl"
        new_path = args.baseline / strategy / "retrieval_results.jsonl"
        old = [json.loads(line) for line in old_path.read_text(encoding="utf-8").splitlines()]
        new = [json.loads(line) for line in new_path.read_text(encoding="utf-8").splitlines()]
        def retrieval_only(row):
            return {"question_id": row["question_id"], "question": row["question"], "candidate_count": row["candidate_count"],
                    **{unit: [{key: value for key, value in portable_record(r).items() if key != "matched_evidence"}
                              for r in row[unit]] for unit in ("children", "parents")}}
        same = [retrieval_only(row) for row in old] == [retrieval_only(row) for row in new]
        if not same:
            raise ValueError(f"Unexpected retrieval change in source-audit experiment: {strategy}")
        old_label_scores = {"child": [], "parent": []}
        current_questions = {q.id: q for q in dataset.questions}
        for row in old:
            if not row["answerable"]:
                continue
            question = current_questions[row["question_id"]].model_copy(update={
                "relevant_evidence": [Evidence.model_validate(e) for e in row["expected_evidence"]]})
            qrels = derive_qrels(question, units)
            grades = {e.evidence_id: e.relevance_grade for e in question.relevant_evidence}
            for unit, score_name in (("children", "child"), ("parents", "parent")):
                matches = [map_evidence(result, question.relevant_evidence) for result in row[unit]]
                old_label_scores[score_name].append(retrieval_metrics(matches, grades, 5,
                    ideal_result_grades=list(qrels[unit].values())))
        def averages(scores):
            return {key: mean(s[key] for s in scores) for key in ("recall", "precision", "mrr", "ndcg")}
        original_metrics = json.loads((args.previous / strategy / "metrics.json").read_text(encoding="utf-8"))["overall"]
        updated_metrics = json.loads((args.baseline / strategy / "metrics.json").read_text(encoding="utf-8"))["overall"]
        reconciliation[strategy] = {
            "fixed_queries_index_rankings_and_scores": True,
            "v01_labels_v01_metrics": {unit: original_metrics[unit] for unit in ("child", "parent")},
            "v01_labels_v2_metrics": {unit: averages(scores) for unit, scores in old_label_scores.items()},
            "v02_labels_v2_metrics": {unit: updated_metrics[unit] for unit in ("child", "parent")},
            "interpretation": "Column 1->2 changes metric definitions only; 2->3 changes annotations only. Neither changes retrieval.",
        }
        comparisons[strategy] = {"all_queries_ranks_scores_and_contents_unchanged": same,
                                "previous_dataset_is_different": True, "metric_contract_changed": True,
                                "score_change_is_not_algorithm_gain": True}
    output = args.baseline
    write_json(output / "source_audit.json", {"dataset_sha256": dataset.sha256, "notes_sha256": checksum(notes_path),
               "questions": source_checks, "all_source_locations_valid": True,
               "all_positive_facts_reachable_in_index": all(not q["unreachable_positive_facts"] for q in source_checks),
               "human_review_pending": dataset.pending_count})
    write_json(output / "failure_diagnostics.json", diagnostics)
    write_json(output / "retrieval_unchanged.json", comparisons)
    write_json(output / "score_reconciliation.json", reconciliation)
    print(f"Audited {len(source_checks)} questions; {sum(len(q['anchors']) for q in source_checks)} anchors; human pending={dataset.pending_count}.")
    for row in diagnostics:
        if row["variant"] != "original":
            print(row["question_id"], row["strategy"], row["variant"], "first relevant candidate", row["first_positive_candidate_rank"])


if __name__ == "__main__":
    main()

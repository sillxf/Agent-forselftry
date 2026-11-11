"""Trace every missing fact to frozen source blocks, indexed units and candidate ranks."""
import argparse
import hashlib
import json
import re
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
from evaluation.rag.dataset import Dataset, checksum
from evaluation.rag.runner import evaluation_units, map_evidence, portable_record, write_json
from app.rag.retriever import KnowledgeRetriever

TAXONOMY = ["Lexical Mismatch", "Semantic Mismatch", "Cross-lingual Retrieval Failure",
    "Chunk Boundary Problem", "Parent Recovery Problem", "Metadata / Structure Problem",
    "Ranking Problem", "Evidence Annotation Problem"]


def diagnose(question, row, candidates, units):
    missing = set(row["diagnostics"]["missing_child_facts"])
    first = next((i for i, r in enumerate(candidates, 1) if map_evidence(r, question.relevant_evidence)), None)
    candidate_hits = {key for r in candidates for key in map_evidence(r, question.relevant_evidence)}
    indexed_hits = {key for r in units["children"] for key in map_evidence(r, question.relevant_evidence)}
    required = {e.evidence_id for e in question.relevant_evidence if e.relevance_grade > 0}
    categories, reasons, suggestions = [], [], []
    if required - indexed_hits:
        categories.append("Chunk Boundary Problem")
        reasons.append("Validated source exists, but some fact quotes do not survive inside any indexed child.")
        suggestions.append("Inspect split boundaries before changing retrieval or annotations.")
    if missing & candidate_hits or first is not None and first > 1:
        categories.append("Ranking Problem")
        reasons.append(f"First relevant configured-pool candidate rank={first}; missing Top-K facts={sorted(missing)}.")
        suggestions.append("Inspect candidate ordering and source context; do not assume a reranker helps.")
    if missing - candidate_hits and not required - indexed_hits:
        chinese_query = bool(re.search(r"[\u3400-\u9fff]", question.question))
        chinese_source = any(re.search(r"[\u3400-\u9fff]", a.text_quote) for e in question.relevant_evidence for a in e.anchors())
        category = "Cross-lingual Retrieval Failure" if chinese_query and not chinese_source else (
            "Lexical Mismatch" if row["strategy"] == "bm25" else "Semantic Mismatch")
        categories.append(category)
        reasons.append("Relevant indexed evidence did not enter the configured candidate pool; language/wording is a hypothesis, not proof.")
        suggestions.append("Use the separate original/translated/multilingual/dual-route experiment, keeping original queries unchanged.")
    if row["diagnostics"]["child_only_facts"]:
        categories.append("Parent Recovery Problem")
        reasons.append("A child supports a fact missing from the independently truncated parent ranking.")
        suggestions.append("Inspect unique-parent grouping and truncation, without mixing child and parent metrics.")
    return dict(categories=categories, reasons=reasons, suggestions=suggestions,
        classification_status="evidence-based ranking diagnostics; language/lexical/semantic causes remain hypotheses",
        first_positive_candidate_rank=first, missing_top_k_fact_ids=sorted(missing),
        missing_configured_candidate_fact_ids=sorted(required-candidate_hits), unreachable_child_fact_ids=sorted(required-indexed_hits))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--storage-dir", type=Path, required=True)
    args = parser.parse_args()
    output = args.baseline
    base = json.loads((output / "hybrid/config.json").read_text(encoding="utf8"))
    dataset = Dataset(output / "annotation_snapshot/questions.jsonl")
    dataset.validate_corpus()
    if dataset.sha256 != base["dataset"]["sha256"]:
        raise ValueError("Frozen annotations do not match saved rankings")
    # Load the original source location for cache reuse; validate identical corpus bytes separately.
    original = Dataset(base["dataset"]["path"])
    original.validate_corpus()
    if checksum(original.manifest_path) != checksum(dataset.manifest_path):
        raise ValueError("Original and frozen corpus manifests differ")
    chunk = base["chunking"]
    retriever = KnowledgeRetriever(knowledge_dir=original.documents_dir, storage_dir=args.storage_dir,
        model_name=base["embedding"]["name"], parent_max_tokens=chunk["parent_max_tokens"],
        child_max_tokens=chunk["child_max_tokens"], overlap_tokens=chunk["overlap_tokens"],
        dense_top_k=base["retrieval"]["dense_top_k"], bm25_top_k=base["retrieval"]["bm25_top_k"])
    dataset.validate_index(retriever)
    fingerprint = hashlib.sha256(json.dumps([portable_record(r) for r in retriever.store.records], sort_keys=True,
        ensure_ascii=False,separators=(",", ":")).encode()).hexdigest()
    if fingerprint != base["index"]["portable_chunks_sha256"]:
        raise ValueError("Failure analysis must use the exact experiment chunks")
    units = evaluation_units(retriever)
    questions = {q.id:q for q in dataset.questions}
    mapping=[]
    for question in dataset.questions:
        facts=[]
        for evidence in question.relevant_evidence:
            anchors=[]
            for anchor in evidence.anchors():
                single=evidence.model_copy(update={**anchor.model_dump(),"alternatives":[]})
                anchors.append(dict(source=anchor.model_dump(), child_ids=[r["chunk_id"] for r in units["children"] if map_evidence(r,[single])],
                    parent_ids=[r["parent_id"] for r in units["parents"] if map_evidence(r,[single])]))
            facts.append(dict(evidence_id=evidence.evidence_id, relevance_grade=evidence.relevance_grade, anchors=anchors))
        mapping.append(dict(question_id=question.id, facts=facts))
    failures,unknown=[],[]
    for strategy in ("dense","bm25","hybrid"):
        config=json.loads((output/strategy/"config.json").read_text(encoding="utf8"))
        for field in ("dataset","corpus","chunking","embedding","index","metric_contract"):
            if config[field]!=base[field]: raise ValueError(f"Strategies differ in {field}")
        rows=[json.loads(line) for line in (output/strategy/"retrieval_results.jsonl").read_text(encoding="utf8").splitlines()]
        for row in rows:
            row["strategy"]=strategy
            question=questions[row["question_id"]]
            if not question.answerable:
                unknown.append(dict(question_id=question.id,query=question.question,strategy=strategy,
                    absence_rationale=question.rationale, expected_evidence_scope="observed_event" if question.id in {"rag_028","rag_030"} else "private_or_missing_reference_data",
                    actual_top_k={unit:row[unit] for unit in ("children","parents")},
                    potentially_misleading_neighbours=bool(row["children"] or row["parents"]),
                    retrieval_assessment="Neighbours cannot establish the missing named entity/incident/private fact; not a generated answer.",
                    knowledge_gap_detection="not_evaluated", hallucination_or_abstention="not_evaluated_agent_task"))
            elif row["failure_types"]:
                # Reproduce the original configured candidate pool, NOT a larger K*4 search.
                candidates=[dict(r,source_block_ids=r["block_ids"]) for r in retriever._rank_children(question.question,config["retrieval"]["top_k"],strategy)]
                failures.append(dict(question_id=question.id,query=question.question,strategy=strategy,
                    correct_evidence=[e.model_dump() for e in question.relevant_evidence], derived_qrels=row["derived_qrels"],
                    actual_top_k={unit:row[unit] for unit in ("children","parents")}, diagnostics=row["diagnostics"],
                    candidate_ranks=[dict(rank=i,chunk_id=r["chunk_id"],matched_evidence=map_evidence(r,question.relevant_evidence)) for i,r in enumerate(candidates,1)],
                    **diagnose(question,row,candidates,units)))
    write_json(output/"evidence_mapping.json",dict(dataset_sha256=dataset.sha256,all_source_anchors_valid=True,questions=mapping))
    write_json(output/"failure_analysis.json",failures)
    write_json(output/"unanswerable_analysis.json",unknown)
    counts=Counter(c for r in failures for c in r["categories"])
    lines=["# 失败定位（不修改题目或检索设置）","","所有分类基于源引用、完整索引、原始 Top K 和相同候选池；原因推断不是已证实的模型缺陷。","", "## 分类统计（题目 × 策略，可多分类）",""]
    lines += [f"- {category}: {counts[category]}" for category in TAXONOMY]
    lines += ["", "## 失败案例", ""]
    for row in failures:
        lines += [f"### {row['question_id']} / {row['strategy']}","",row["query"],
            f"- 分类：{', '.join(row['categories']) or 'inspect raw results'}",
            f"- 正确候选首次排名：{row['first_positive_candidate_rank']}",
            f"- Child Top K 缺少事实：{row['missing_top_k_fact_ids']}",
            *["- 原因："+s for s in row["reasons"]], *["- 建议："+s for s in row["suggestions"]], ""]
    lines += ["## 不可回答题", "", "15 条题目×策略记录保留了真实邻近结果；不能据此声称 Agent 能拒答或检测知识缺口。", "查看 unanswerable_analysis.json 和后续 Agent Evaluation 设计。", "", "完整 Chunk、来源、Block ID、候选排名和必要事实见 JSON；与历史标签错误分开记录。", ""]
    (output/"failure_analysis.md").write_text("\n".join(lines),encoding="utf8")
    print(f"Mapped {len(mapping)} questions; {len(failures)} failed query/strategy pairs; {len(unknown)} unknown pairs.")


if __name__ == "__main__":
    main()

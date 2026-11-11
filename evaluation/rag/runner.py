"""Run real retrieval once per question and preserve both ranking units and errors."""
import hashlib
import json
import time

from evaluation.rag.dataset import normalize
from evaluation.rag.metrics import retrieval_metrics
from evaluation.rag.multik import failure_analysis


def map_evidence(result, evidence):
    """Block identity AND a source quote must occur in the actual returned text.

    Child block_ids currently describe a whole source group, so ID overlap alone
    could credit a different slice or table row. Quotes guard against that inflation.
    """
    ids = set(result["source_block_ids"])
    content = normalize(result["content"])
    return [e.evidence_id for e in evidence if any(
        a.document_id == result["document_id"] and ids & set(a.source_block_ids)
        and normalize(a.text_quote) in content for a in e.anchors())]


def annotate(results, question, retriever, *, parent=False):
    output = []
    for rank, source in enumerate(results, 1):
        result = dict(source)
        if parent:
            blocks = retriever.parents[result["parent_id"]].blocks
            result["source_block_ids"] = list(dict.fromkeys(
                key for block in blocks for key in (block.source_block_ids or [block.block_id])))
        result["rank"] = rank
        result["matched_evidence"] = map_evidence(result, question.relevant_evidence)
        output.append(result)
    return output


def evaluation_units(retriever):
    """The complete indexed universe, independent of query strategy and returned ranks."""
    children = [dict(item, source_block_ids=item["block_ids"]) for item in retriever.store.records]
    parents = [{"parent_id": p.parent_id, "document_id": p.document_id, "content": p.content,
                "source_block_ids": list(dict.fromkeys(key for b in p.blocks
                    for key in (b.source_block_ids or [b.block_id])))} for p in retriever.parents.values()]
    return {"children": children, "parents": parents}


def derive_qrels(question, units):
    """Map source annotations to each indexed unit; these are derived, not human chunk labels."""
    grades = {e.evidence_id: e.relevance_grade for e in question.relevant_evidence}
    qrels = {}
    for name, records in units.items():
        id_field = "chunk_id" if name == "children" else "parent_id"
        qrels[name] = {}
        for record in records:
            matches = map_evidence(record, question.relevant_evidence)
            grade = max((grades[key] for key in matches), default=0)
            if grade > 0:
                qrels[name][record[id_field]] = grade
    return qrels


def ranking_diagnostics(question, children, parents, qrels):
    """Body-evidence coverage only; a returned neighbour is not a generated answer."""
    required = {e.evidence_id for e in question.relevant_evidence if e.relevance_grade > 0}
    child_hits = {key for r in children for key in r["matched_evidence"]} & required
    parent_hits = {key for r in parents for key in r["matched_evidence"]} & required
    return {
        "child_only_facts": sorted(child_hits - parent_hits),
        "parent_only_facts": sorted(parent_hits - child_hits),
        "missing_child_facts": sorted(required - child_hits),
        "missing_parent_facts": sorted(required - parent_hits),
        "positive_children_outside_top_k": sorted(set(qrels["children"]) - {r["chunk_id"] for r in children}),
        "positive_parents_outside_top_k": sorted(set(qrels["parents"]) - {r["parent_id"] for r in parents}),
        "nonrelevant_child_ranks": [r["rank"] for r in children if not required & set(r["matched_evidence"])],
        "nonrelevant_parent_ranks": [r["rank"] for r in parents if not required & set(r["matched_evidence"])],
        "unanswerable_assessment": None if question.answerable else {
            "returned_neighbour_context": bool(children or parents),
            "answer_support_in_frozen_corpus": False,
            "false_analogy_risk": "requires_case_review" if children or parents else "no_context_returned",
            "knowledge_gap_detection": "not_evaluated",
            "incorrect_answer_or_refusal": "not_evaluated_retrieval_only",
        },
    }


def run_benchmark(dataset, retriever, *, top_k=5, strategy="hybrid", evaluation_ks=None, ranker=None):
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    dataset.validate_corpus()
    dataset.validate_index(retriever)
    ks = sorted(set(evaluation_ks or [top_k]))
    if any(k <= 0 for k in ks):
        raise ValueError("Evaluation K values must be positive")
    depth = max(top_k, *ks)
    retrieve = ranker or retriever.search_rankings
    rows = []
    units = evaluation_units(retriever)
    for question in dataset.questions:
        qrels = derive_qrels(question, units)
        started = time.perf_counter()
        error, child, parent, candidate_count = None, [], [], 0
        ranks = {}
        try:
            # Only the question is queried. Never concatenate answers or evidence labels.
            ranks = retrieve(question.question, depth, strategy)
            latency_ms = (time.perf_counter() - started) * 1000
            candidate_count = ranks["candidate_count"]
            child = annotate(ranks["children"], question, retriever)
            parent = annotate(ranks["parents"], question, retriever, parent=True)
        except Exception as exception:
            # Per-query errors are preserved and scored as misses, never silently dropped.
            latency_ms = (time.perf_counter() - started) * 1000
            error = f"{type(exception).__name__}: {exception}"
            child, parent = [], []
        grades = {e.evidence_id: e.relevance_grade for e in question.relevant_evidence}
        child_metrics = retrieval_metrics([r["matched_evidence"] for r in child], grades, top_k,
                                          ideal_result_grades=list(qrels["children"].values()))
        parent_metrics = retrieval_metrics([r["matched_evidence"] for r in parent], grades, top_k,
                                           ideal_result_grades=list(qrels["parents"].values()))
        by_k = {str(k): {name: retrieval_metrics([r["matched_evidence"] for r in ranked], grades, k,
                    ideal_result_grades=list(qrels[universe].values()))
                    for name, universe, ranked in (("child", "children", child), ("parent", "parents", parent))}
                for k in ks}
        analysis = failure_analysis(question, child, parent, top_k, depth, error)
        failures = []
        if error:
            failures.append("retrieval_error")
        elif question.answerable:
            if child_metrics["recall"] == 0:
                failures.append("no_relevant_child")
            elif child_metrics["recall"] < 1:
                failures.append("partial_evidence")
            if child_metrics["mrr"] < 1:
                failures.append("first_result_not_relevant")
            if parent_metrics["recall"] < 1:
                failures.append("incomplete_parent_context")
        rows.append({
            "question_id": question.id, "question": question.question, "category": question.category,
            "difficulty": question.difficulty, "answerable": question.answerable,
            "review_status": question.review_status, "expected_answer": question.expected_answer,
            "language": question.language or "unspecified", "document_language": question.document_language or "unspecified",
            "topic": question.topic or question.category, "question_type": question.question_type or question.category,
            "language_pair": f"{question.language or 'unspecified'}->{question.document_language or 'unspecified'}",
            "strategy": strategy, "query_routes": ranks.get("query_routes", []), "ranking_depth": depth, "metrics_by_k": by_k, "failure_analysis": analysis,
            "document_types": sorted({a.source.rsplit(".", 1)[-1] for e in question.relevant_evidence for a in e.anchors()}),
            "expected_evidence": [e.model_dump() for e in question.relevant_evidence],
            "latency_ms": latency_ms, "candidate_count": candidate_count,
            "children": child, "parents": parent,
            "child_metrics": child_metrics, "parent_metrics": parent_metrics, "derived_qrels": qrels,
            "parent_context_characters": sum(len(r["content"]) for r in parent),
            "error": error, "failure_types": failures,
            "diagnostics": ranking_diagnostics(question, child[:top_k], parent[:top_k], qrels),
        })
    return rows


def write_json(path, value):
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2, allow_nan=False) + "\n", encoding="utf-8")


def portable_record(record):
    """Image locations are storage-local; their document hash/file suffix is stable."""
    result = dict(record)
    if "image_paths" in result:
        result["image_paths"] = ["/".join(path.replace("\\", "/").split("/")[-2:])
                                 for path in result["image_paths"]]
    return result


def ranking_fingerprint(rows):
    """Compare semantic ranks, scores and metrics, excluding timing and local storage paths."""
    stable = [{"question_id": row["question_id"], "candidate_count": row["candidate_count"],
               "children": [portable_record(r) for r in row["children"]],
               "parents": [portable_record(r) for r in row["parents"]],
               "child_metrics": row["child_metrics"], "parent_metrics": row["parent_metrics"],
               "derived_qrels": row["derived_qrels"], "error": row["error"], "failure_types": row["failure_types"]} for row in rows]
    return hashlib.sha256(json.dumps(stable, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()

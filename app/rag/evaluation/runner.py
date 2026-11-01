"""Run real retrieval once per question and preserve both ranking units and errors."""
import hashlib
import json
import time

from app.rag.evaluation.dataset import normalize
from app.rag.evaluation.retrieval_metrics import retrieval_metrics


def map_evidence(result, evidence):
    """Block identity AND a source quote must occur in the actual returned text.

    Child block_ids currently describe a whole source group, so ID overlap alone
    could credit a different slice or table row. Quotes guard against that inflation.
    """
    ids = set(result["source_block_ids"])
    content = normalize(result["content"])
    return [e.evidence_id for e in evidence
            if e.document_id == result["document_id"] and ids & set(e.source_block_ids)
            and normalize(e.text_quote) in content]


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


def run_benchmark(dataset, retriever, *, top_k=5, strategy="hybrid"):
    if top_k <= 0:
        raise ValueError("top_k must be positive")
    dataset.validate_corpus()
    dataset.validate_index(retriever)
    rows = []
    for question in dataset.questions:
        started = time.perf_counter()
        error, child, parent, candidate_count = None, [], [], 0
        try:
            # Only the question is queried. Never concatenate answers or evidence labels.
            ranks = retriever.search_rankings(question.question, top_k, strategy)
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
        child_metrics = retrieval_metrics([r["matched_evidence"] for r in child], grades, top_k)
        parent_metrics = retrieval_metrics([r["matched_evidence"] for r in parent], grades, top_k)
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
            "review_status": question.review_status,
            "document_types": sorted({e.source.rsplit(".", 1)[-1] for e in question.relevant_evidence}),
            "expected_evidence": [e.model_dump() for e in question.relevant_evidence],
            "latency_ms": latency_ms, "candidate_count": candidate_count,
            "children": child, "parents": parent,
            "child_metrics": child_metrics, "parent_metrics": parent_metrics,
            "parent_context_characters": sum(len(r["content"]) for r in parent),
            "error": error, "failure_types": failures,
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
               "error": row["error"], "failure_types": row["failure_types"]} for row in rows]
    return hashlib.sha256(json.dumps(stable, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":"), allow_nan=False).encode()).hexdigest()

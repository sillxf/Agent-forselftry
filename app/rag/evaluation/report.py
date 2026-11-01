"""Transparent macro averages, explicit no-answer accounting and failure reports."""
from collections import defaultdict
from statistics import mean

import numpy as np

from app.rag.evaluation.runner import write_json
from app.rag.evaluation.retrieval_metrics import METRIC_CONTRACT


def summarize(rows):
    answerable = [row for row in rows if row["answerable"]]
    unanswerable = [row for row in rows if not row["answerable"]]
    return {
        "questions": len(rows), "answerable": len(answerable), "unanswerable": len(unanswerable),
        "pending_human_review": sum(row["review_status"] != "approved" for row in rows),
        "errors": sum(row["error"] is not None for row in rows),
        "child": {key: mean(r["child_metrics"][key] for r in answerable) if answerable else None
                  for key in ("recall", "precision", "mrr", "ndcg")},
        "parent": {key: mean(r["parent_metrics"][key] for r in answerable) if answerable else None
                   for key in ("recall", "precision", "mrr", "ndcg")},
        "latency_ms": {"mean": mean(r["latency_ms"] for r in rows),
                       "p50": float(np.percentile([r["latency_ms"] for r in rows], 50)),
                       "p95": float(np.percentile([r["latency_ms"] for r in rows], 95))},
        "mean_candidate_count": mean(r["candidate_count"] for r in rows),
        "no_result_rate": mean(not r["children"] for r in rows),
        "coverage_diagnostics": {
            "child_hit_parent_miss_questions": sum(bool(r["diagnostics"]["child_only_facts"]) for r in answerable),
            "parent_hit_child_miss_questions": sum(bool(r["diagnostics"]["parent_only_facts"]) for r in answerable),
            "missing_child_evidence_questions": sum(bool(r["diagnostics"]["missing_child_facts"]) for r in answerable),
            "nonrelevant_top_k_child_results": sum(len(r["diagnostics"]["nonrelevant_child_ranks"]) for r in answerable),
        },
        "unanswerable_stats": {
            "questions": len(unanswerable),
            "returned_context_count": sum(bool(r["parents"]) for r in unanswerable),
            "no_result_count": sum(not r["parents"] for r in unanswerable),
            "correct_refusal_rate": None,
            "reason": "Retrieval-only benchmark; returning a neighbour is not an answer or refusal.",
        },
        "mean_parent_context_characters": mean(r["parent_context_characters"] for r in rows),
    }


def build_report(output, config, rows):
    groups = {}
    for field in ("category", "difficulty", "document_types"):
        buckets = defaultdict(list)
        for row in rows:
            values = row[field] if field == "document_types" else [row[field]]
            for key in values:
                buckets[key].append(row)
        groups[field] = {key: summarize(items) for key, items in sorted(buckets.items())}
    metrics = {"metric_contract": METRIC_CONTRACT, "overall": summarize(rows), "groups": groups}
    failures = [row for row in rows if row["failure_types"]]
    write_json(output / "metrics.json", metrics)
    write_json(output / "failures.json", failures)
    write_json(output / "diagnostics.json", [{"question_id": r["question_id"], **r["diagnostics"]} for r in rows])
    overall = metrics["overall"]
    k = config["retrieval"]["top_k"]
    lines = [f"# {config['retrieval']['strategy']} retrieval baseline", "",
             f"Status: **{config['annotation_status']}**; {overall['pending_human_review']} labels pending human review.",
             f"Dataset: `{config['dataset']['version']}` / `{config['dataset']['sha256']}`.",
             f"Code: `{config['code']['commit']}`; dirty={config['code']['dirty']}; source SHA-256 `{config['code']['source_sha256']}`.",
             "", f"Questions: {overall['questions']}; answerable: {overall['answerable']}; unanswerable: {overall['unanswerable']}.",
             "", f"| Ranking unit (K={k}) | Evidence Recall | Result Precision | MRR | Result NDCG |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for unit in ("child", "parent"):
        m = overall[unit]
        formatted = [f"{m[key]:.4f}" if m[key] is not None else "N/A" for key in ("recall", "precision", "mrr", "ndcg")]
        lines.append(f"| {unit} | " + " | ".join(formatted) + " |")
    lines += ["", "Child K and unique-parent K are different ranking units; do not combine them.",
              f"Metric contract: `{METRIC_CONTRACT}`. Recall covers unique required facts; alternatives are OR locations.",
              "Precision is relevant result slots / fixed K. Multiple distinct results supporting one fact remain relevant.",
              "DCG uses max fact grade per result, gain 2^grade-1 and log2(rank+1) discount.",
              "IDCG uses the sorted grades of ALL indexed units of the same type, not the number of facts.",
              "Qrels are deterministically derived from body quotes and source IDs, not independently human-judged chunks.",
              "Misses keep their rank. Metadata-only answers are not credited as body evidence.",
              "Old v0.1 novelty/evidence metrics used a different definition and are not directly comparable.",
              "No search, embedding, chunking or RRF change is implied by an evaluation score change.",
              "", "## Categories", "", "| Category | Questions | Child Recall | Child MRR | Parent Recall |",
              "| --- | ---: | ---: | ---: | ---: |"]
    for key, value in groups["category"].items():
        fmt = lambda number: f"{number:.4f}" if number is not None else "N/A"
        lines.append(f"| {key} | {value['questions']} | {fmt(value['child']['recall'])} | {fmt(value['child']['mrr'])} | {fmt(value['parent']['recall'])} |")
    lines += ["", "## Engineering diagnostics", "",
              f"Errors: {overall['errors']}; no-result rate: {overall['no_result_rate']:.4f}.",
              f"Retrieval latency ms (mean/P50/P95): {overall['latency_ms']['mean']:.2f} / {overall['latency_ms']['p50']:.2f} / {overall['latency_ms']['p95']:.2f}.",
              "Latency excludes model/index setup and evidence scoring. The first query is not warmed separately.",
              f"Mean parent context length: {overall['mean_parent_context_characters']:.1f} characters.",
              "This is a size diagnostic, not a validated context-noise/precision metric.",
              "Unanswerable cases are excluded from ranking averages; no refusal rate is inferred.",
              "", "## Failures", ""]
    lines += [f"- `{r['question_id']}`: {', '.join(r['failure_types'])} — {r['question']}" for r in failures] or ["None."]
    lines += ["", "## Scope and limitations", "",
              "All source evidence and quotes were checked against the actual index before evaluation.",
              "Pending labels are AI-prepared candidates, not human-certified ground truth. Review alternative",
              "valid sources, grades and unanswerable rationales before treating these scores as acceptance results.",
              "This small development set is not a holdout benchmark and does not establish general accuracy.",
              "No LLM answer generation, judge, reranker, embedding migration or automatic tuning was performed.",
              "Read `retrieval_results.jsonl` and `failures.json` for full ranks, scores, quotes and provenance."]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return metrics

"""Multi-K and grouped retrieval reports; no answer/Agent refusal judging."""
import json
from collections import defaultdict
from statistics import mean


def failure_analysis(question, children, parents, cutoff, depth, error):
    required = set(question.evidence_ids)
    details = {}
    for name, ranking in (("child", children), ("parent", parents)):
        hits = {fact for row in ranking[:cutoff] for fact in row["matched_evidence"]} & required
        later = {fact for row in ranking[cutoff:] for fact in row["matched_evidence"]} & required
        negatives = [row["rank"] for row in ranking[:cutoff] if row.get("source_name", row.get("source")) in question.hard_negative_sources]
        reasons = []
        if error:
            reasons.append("query_execution_error")
        elif required - hits:
            reasons.append("relevant_evidence_ranked_below_cutoff" if (required-hits) & later else f"required_evidence_absent_from_saved_top_{depth}")
        if negatives:
            reasons.append("known_similar_but_wrong_source_returned")
        if required-hits and question.language in {"zh", "mixed"} and question.document_language == "en":
            reasons.append("cross_language_mismatch_hypothesis_not_proven")
        details[name] = dict(missing_evidence_ids=sorted(required-hits),
                             recovered_below_cutoff=sorted((required-hits) & later),
                             first_relevant_rank=next((r["rank"] for r in ranking if set(r["matched_evidence"]) & required), None),
                             hard_negative_ranks=negatives, reasons=reasons,
                             reason_scope="Only saved ranks and declared hard negatives are observed; embedding/lexical cause needs controlled comparison.")
    return details


def aggregate(rows, ks):
    positive = [r for r in rows if r["answerable"]]
    negative = [r for r in rows if not r["answerable"]]
    return dict(questions=len(rows), answerable=len(positive), unanswerable=len(negative),
                by_k={str(k): {unit: {metric: mean(r["metrics_by_k"][str(k)][unit][metric] for r in positive) if positive else None
                                     for metric in ("recall", "precision", "mrr", "ndcg")}
                               for unit in ("child", "parent")} for k in ks},
                unanswerable_stats=dict(questions=len(negative),
                    unrelated_context_return_rate=mean(bool(r["parents"]) for r in negative) if negative else None,
                    returned_context_questions=[r["question_id"] for r in negative if r["parents"]],
                    false_positive_high_relevance_judgment=None, correct_refusal_rate=None,
                    note="No relevance threshold, answerability classifier, generator or Agent judge is used. Returned context is not an accepted answer."))


def export_extended(output, config, rows):
    ks = sorted(map(int, rows[0]["metrics_by_k"]))
    groups = {}
    for field in ("question_type", "language_pair", "language", "difficulty", "topic"):
        buckets = defaultdict(list)
        for row in rows:
            buckets[row[field]].append(row)
        groups[field] = {key: aggregate(items, ks) for key, items in sorted(buckets.items())}
    groups["multi_document_required"] = aggregate([r for r in rows if len({e["document_id"] for e in r["expected_evidence"]}) > 1], ks)
    report = dict(metric_contract="result-qrels-v2", evaluation_ks=ks, ranking_depth=max(r["ranking_depth"] for r in rows),
                  prefix_policy="One ranking to maximum K; all smaller K values are prefixes. Candidate pools are chosen for that depth, not the historical smaller-K run.",
                  overall=aggregate(rows, ks), groups=groups)
    (output / "multik_metrics.json").write_text(json.dumps(report, ensure_ascii=False, indent=2)+"\n", encoding="utf-8")
    lines = ["# Multi-K retrieval and grouped metrics", "", "Candidate labels; no generated-answer accuracy or Agent refusal claim.", "",
             "One shared maximum-depth ranking. Child and unique-Parent are different ranking universes.", "",
             "| Unit | Recall@1 | Recall@3 | Recall@5 | Recall@10 | Precision@5 | MRR@5 | NDCG@5 |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    def metric(unit, k, name, summary):
        value = summary["by_k"].get(str(k), {}).get(unit, {}).get(name)
        return "N/A" if value is None else f"{value:.4f}"
    for unit in ("child", "parent"):
        values = [metric(unit,k,"recall",report["overall"]) for k in (1,3,5,10)] + [metric(unit,5,m,report["overall"]) for m in ("precision","mrr","ndcg")]
        lines.append(f"| {unit} | " + " | ".join(values) + " |")
    lines += ["", "## Groups (Parent metrics)", "", "| Dimension | Group | N | Recall@1 | Recall@3 | Recall@5 | Recall@10 | MRR@5 |", "| --- | --- | --- | --- | --- | --- | --- | --- |"]
    for field in ("question_type", "language_pair", "difficulty"):
        for key, summary in groups[field].items():
            values = [metric("parent",k,"recall",summary) for k in (1,3,5,10)] + [metric("parent",5,"mrr",summary)]
            lines.append(f"| {field} | {key} | {summary['questions']} | " + " | ".join(values) + " |")
    lines += ["", "Unknown questions are excluded from ordinary Recall/MRR. Their unrelated-context return rate is saved separately; it is not an Agent false-answer or refusal rate."]
    (output / "multik_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    failures = [r for r in rows if r["error"] or not r["answerable"] or any(r["failure_analysis"][u]["reasons"] for u in ("child","parent"))]
    (output / "failure_cases.json").write_text(json.dumps(failures,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    lines = ["# Per-question retrieval failures, context noise and unknown cases", "", "Observed ranks are distinguished from unproven semantic-cause hypotheses.", ""]
    for r in failures:
        lines += [f"## {r['question_id']} — {r['strategy']}", "", r["question"], "", f"Reference: {r['expected_answer']}",
                  f"Answerable: {r['answerable']}; type={r['question_type']}; language={r['language_pair']}", ""]
        for unit, name in (("child","children"),("parent","parents")):
            lines += [f"### {unit}", json.dumps(r["failure_analysis"][unit],ensure_ascii=False), "",
                      "| Rank | Source | Retrieved unit ID | Matched gold Evidence IDs |", "| --- | --- | --- | --- |"]
            for item in r[name]:
                identifier=item["chunk_id"] if unit=="child" else item["parent_id"]
                lines.append(f"| {item['rank']} | {item.get('source_name',item.get('source'))} | `{identifier}` | {', '.join(item['matched_evidence']) or 'none'} |")
        lines.append("")
    (output / "failure_report.md").write_text("\n".join(lines)+"\n",encoding="utf-8")
    return report

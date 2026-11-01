"""A/B/C tables from frozen retrieval outputs; no generation or answer judging."""
import argparse
import json
from pathlib import Path
from statistics import mean

import numpy as np

from evaluation.rag.dataset import checksum
from evaluation.rag.runner import write_json


def load_json(path):
    return json.loads(path.read_text(encoding="utf-8"))


def latency(rows):
    values = [r["latency_ms"] for r in rows]
    return {"queries": len(values), "mean_ms": mean(values),
            "p50_ms": float(np.percentile(values, 50)),
            "p95_ms": float(np.percentile(values, 95)),
            "total_seconds": sum(values) / 1000} if values else None


def build_comparison_report(baseline, output):
    baseline, output = Path(baseline), Path(output)
    folders = {"A": baseline / "hybrid", "B": output / "B", "C": output / "C"}
    arms = {}
    for label, folder in folders.items():
        config = load_json(folder / "config.json")
        metrics = load_json(folder / "multik_metrics.json")
        rows = [json.loads(line) for line in (folder / "retrieval_results.jsonl").read_text(encoding="utf-8").splitlines()]
        arms[label] = dict(folder=str(folder.resolve()), config=config, metrics=metrics, rows=rows)
    reference = arms["A"]["config"]
    for label, arm in arms.items():
        assert arm["config"]["dataset"]["sha256"] == reference["dataset"]["sha256"], label
        assert arm["config"]["corpus"]["manifest_sha256"] == reference["corpus"]["manifest_sha256"], label
        assert arm["config"]["chunking"] == reference["chunking"], label
        assert arm["config"]["index"]["portable_chunks_sha256"] == reference["index"]["portable_chunks_sha256"], label
        assert [(r["question_id"], r["question"], r["expected_evidence"]) for r in arm["rows"]] == [(r["question_id"], r["question"], r["expected_evidence"]) for r in arms["A"]["rows"]], label
    summary = dict(dataset_sha256=reference["dataset"]["sha256"],
                   corpus_manifest_sha256=reference["corpus"]["manifest_sha256"],
                   chunk_texts_and_ids_sha256=reference["index"]["portable_chunks_sha256"],
                   top_k=reference["retrieval"]["top_k"], ranking_depth=reference["retrieval"]["ranking_depth"],
                   unit="unique-parent", generation_evaluated=False, arms={})
    for label, arm in arms.items():
        grouped = arm["metrics"]["groups"]
        summary["arms"][label] = dict(
            model=arm["config"]["embedding"], query_policy=arm["config"].get("query_policy", "original query hybrid"),
            queries=len(arm["rows"]), query_errors=sum(bool(r["error"]) for r in arm["rows"]),
            overall=arm["metrics"]["overall"],
            language_pairs=grouped["language_pair"], question_types=grouped["question_type"],
            latency=latency(arm["rows"]),
            language_latency={key: latency([r for r in arm["rows"] if r["language_pair"] == key]) for key in ("zh->en", "en->en")},
            setup_timing=arm["config"].get("timing"),
            retrieval_results_sha256=checksum(folders[label] / "retrieval_results.jsonl"))
    improvements = {}
    for label in ("B", "C"):
        improvements[label] = {}
        for k, metric in ((5, "recall"), (10, "recall"), (5, "mrr")):
            a = summary["arms"]["A"]["language_pairs"]["zh->en"]["by_k"][str(k)]["parent"][metric]
            b = summary["arms"][label]["language_pairs"]["zh->en"]["by_k"][str(k)]["parent"][metric]
            improvements[label][f"{metric}_at_{k}"] = dict(baseline=a, value=b, percentage_point_change=(b-a)*100, relative_change=(b/a-1) if a else None)
    summary["zh_to_en_improvement_over_A"] = improvements
    c_rows = arms["C"]["rows"]
    positive = [r for r in c_rows if r["answerable"]]
    missed = [r for r in positive if r["metrics_by_k"]["5"]["parent"]["recall"] < 1 or r["error"]]
    details = []
    for row in missed:
        required = {e["evidence_id"] for e in row["expected_evidence"] if e["relevance_grade"] > 0}
        hits5 = {e for r in row["parents"][:5] for e in r["matched_evidence"]} & required
        hits10 = {e for r in row["parents"][:10] for e in r["matched_evidence"]} & required
        reasons = []
        if row["error"]:
            reasons.append("query_execution_error")
        if required - hits10:
            reasons.append("required_facts_absent_from_saved_top10")
        if (required-hits5) & hits10:
            reasons.append("correct_facts_ranked_6_to_10")
        if hits5 and required-hits5:
            reasons.append("partial_coverage_of_required_facts")
        if row["failure_analysis"]["parent"]["hard_negative_ranks"]:
            reasons.append("declared_similar_nonanswer_source_present")
        details.append(dict(question_id=row["question_id"], question=row["question"], language_pair=row["language_pair"],
                            question_type=row["question_type"], expected_answer=row["expected_answer"],
                            recall_at_5=row["metrics_by_k"]["5"]["parent"]["recall"],
                            recall_at_10=row["metrics_by_k"]["10"]["parent"]["recall"],
                            first_positive_rank=row["failure_analysis"]["parent"]["first_relevant_rank"],
                            missing_evidence_at_5=sorted(required-hits5), missing_evidence_at_10=sorted(required-hits10),
                            observed_reasons=reasons,
                            route_gold_child_ranks=[dict(kind=route["kind"], ranks=[item["rank"] for item in route["candidates"] if item["chunk_id"] in row["derived_qrels"]["children"]]) for route in row["query_routes"]],
                            top5_sections=[r.get("section_path", []) for r in row["parents"][:5]],
                            missing_sources=sorted({e["source"] for e in row["expected_evidence"] if e["evidence_id"] not in hits5}),
                            top5_sources=[r.get("source_name", r.get("source")) for r in row["parents"][:5]]))
    summary["C_failures"] = dict(answerable_questions=len(positive), incomplete_at_5=len(missed),
                                  zero_recall_at_10=sum(r["metrics_by_k"]["10"]["parent"]["recall"] == 0 for r in positive),
                                  incomplete_at_10=sum(r["metrics_by_k"]["10"]["parent"]["recall"] < 1 for r in positive))
    write_json(output / "abc_comparison.json", summary)
    write_json(output / "C_failure_analysis.json", details)
    lines = ["# Security RAG Benchmark V1：A/B/C 实测对比", "",
             "A 为已封存的 MiniLM + Hybrid；B 为 BGE-M3 + 同一 Hybrid；C 为 BGE-M3 原问/英文双 Dense + 英文 BM25 + RRF60。", "",
             "同一 100 题、21 份文档、301 个冻结 Child、70 个 Parent；没有修改 Benchmark 或 Ground Truth。",
             "正文以 unique-Parent 的事实覆盖宏平均计分。90 道可回答题进入 Recall/MRR/NDCG；10 道不可答题不进入这些指标。", "",
             "## 1. 全部可回答问题", "", "| 方案 | Recall@5 | Recall@10 | MRR@5 | NDCG@5 | 查询错误 |",
             "| --- | --- | --- | --- | --- | --- |"]
    def value(label, scope, k, name):
        data = summary["arms"][label]
        block = data["overall"] if scope == "overall" else data["language_pairs"][scope]
        return block["by_k"][str(k)]["parent"][name]
    def pct(v):
        return f"{v*100:.2f}%"
    for label in arms:
        vals = [value(label,"overall",5,"recall"),value(label,"overall",10,"recall"),value(label,"overall",5,"mrr"),value(label,"overall",5,"ndcg")]
        lines.append(f"| {label} | " + " | ".join(map(pct, vals)) + f" | {summary['arms'][label]['query_errors']} |")
    for scope, title in (("zh->en", "中文问题 → 英文文档"), ("en->en", "英文问题 → 英文文档")):
        count = summary["arms"]["A"]["language_pairs"][scope]["answerable"]
        lines += ["", f"## {title}（{count} 道可回答题，跨越主分类）", "", "| 方案 | Recall@5 | Recall@10 | MRR@5 |", "| --- | --- | --- | --- |"]
        for label in arms:
            lines.append(f"| {label} | {pct(value(label,scope,5,'recall'))} | {pct(value(label,scope,10,'recall'))} | {pct(value(label,scope,5,'mrr'))} |")
    lines += ["", "## 中文跨语言相对 A 的变化", "", "| 方案 | Recall@5 变化（百分点） | Recall@10 变化（百分点） | MRR@5 变化（百分点） |", "| --- | --- | --- | --- |"]
    for label in ("B", "C"):
        changes = [improvements[label][m]["percentage_point_change"] for m in ("recall_at_5","recall_at_10","mrr_at_5")]
        lines.append(f"| {label} | " + " | ".join(f"{v:+.2f}" for v in changes) + " |")
    lines += ["", "## 检索耗时（毫秒/题）", "", "| 方案 | 全 100 题 mean | p50 | p95 | 中文→英文 mean | 英文→英文 mean |", "| --- | --- | --- | --- | --- | --- |"]
    for label in arms:
        s = summary["arms"][label]
        vals = [s["latency"]["mean_ms"],s["latency"]["p50_ms"],s["latency"]["p95_ms"],s["language_latency"]["zh->en"]["mean_ms"],s["language_latency"]["en->en"]["mean_ms"]]
        lines.append(f"| {label} | " + " | ".join(f"{v:.2f}" for v in vals) + " |")
    lines += ["", "耗时是每题实际在线检索路径，不含 qrels 评分、模型下载/加载和建索引。C 使用已冻结英文 Query，不含翻译生成耗时；这是缓存翻译条件，不是端到端在线翻译性能。",
              "A 为历史运行时间，B/C 为本次运行；后台负载和缓存可能不同。耗时不是受控并发压测，不据此宣称严格倍数。CPU/线程/依赖及 BGE 建索引、加载耗时见各组 config.json。", "",
              "## C 仍失败的典型问题", "",
              f"90 道可回答题中，Top5 必要事实未全覆盖 {len(missed)} 题；Top10 零命中 {summary['C_failures']['zero_recall_at_10']} 题，未全覆盖 {summary['C_failures']['incomplete_at_10']} 题。", ""]
    # Prefer one example per failure pattern/type, then fill remaining slots.
    selected, seen = [], set()
    for row in details:
        key = (tuple(row["observed_reasons"]), row["question_type"])
        if key not in seen:
            selected.append(row); seen.add(key)
    selected = (selected + [r for r in details if r not in selected])[:8]
    labels = {"query_execution_error":"检索执行报错", "required_facts_absent_from_saved_top10":"仍有必要事实未进入保存的 Top10", "correct_facts_ranked_6_to_10":"正确事实落在第 6–10 名", "partial_coverage_of_required_facts":"Top5 只覆盖部分必要事实", "declared_similar_nonanswer_source_present":"Top5 存在预先声明的相似干扰来源"}
    for row in selected:
        lines += [f"### {row['question_id']} — {row['question_type']}", "", row["question"], "",
                  f"- Parent Recall@5 / @10：{pct(row['recall_at_5'])} / {pct(row['recall_at_10'])}；首个正向排名：{row['first_positive_rank']}。",
                  "- 可确认现象：" + "；".join(labels[r] for r in row["observed_reasons"]) + "。",
                  "- 各路标注正向 Child 排名：" + "; ".join(route["kind"] + "=" + (", ".join(map(str, route["ranks"])) or "未在候选内") for route in row["route_gold_child_ranks"]) + "。",
                  "- 未覆盖事实来源：" + ", ".join(row["missing_sources"]) + "。",
                  "- Top5 来源：" + ", ".join(row["top5_sources"]) + "。", ""]
    if not details:
        lines.append("本次 C 没有 Top5 必要事实缺失，未编造失败案例。")
    lines += ["", "上述是从实际排名、证据匹配和已标注干扰来源得出的观察。仅凭排名不能确定模型语义、翻译或 Chunk 边界是哪一个根因；完整原文和排名见 C/retrieval_results.jsonl 与 C/failure_report.md。这里按冻结 Ground Truth 的标注引文严格计分，没有因其他段落看起来相关就临时扩充正向证据。", "",
              "## 复现与边界", "",
              f"- Dataset SHA-256：`{summary['dataset_sha256']}`。",
              f"- BGE revision：`{summary['arms']['B']['model']['resolved_revision']}`。",
              "- 模型、Tokenizer、Chunk/向量和源码 SHA 保存在 config.json；本次英文 Query 在 english_queries.json，逐题翻译调整记录在 translation_changes.json。",
              "- 英文原问与英文翻译相同时去重 Dense 路由；非英文题通常是三路 RRF。",
              "- BGE 仅使用 Dense 向量；BM25 仍是原有 BM25Plus，不是 BGE 原生稀疏或 ColBERT。",
              "- 使用原 MiniLM 冻结 Chunk，控制切分变量；不代表 BGE 所有长文档配置的上限。",
              "- 这仍是公开开发候选集（约 63 个去重文档+引文事实，含语言变体），不能把此处接近满分外推为生产或独立留出集表现。",
              "- 标签仍为原候选审核状态，本次没有开展人工审核；没有生成答案、Cross-Encoder 或 Agent 拒答实验。",
              "- 生产 app/、原 MiniLM 索引和原实验结果没有修改。", ""]
    (output / "abc_report.md").write_text("\n".join(lines), encoding="utf-8")
    return summary


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    build_comparison_report(args.baseline, args.output_dir)


if __name__ == "__main__":
    main()

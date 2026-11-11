"""Evaluate Multi-View as a supplement to Hybrid before BGE reranking."""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

from evaluation.rag.dataset import Dataset, checksum
from evaluation.rag.metrics import METRIC_CONTRACT
from evaluation.rag.model_comparison import load_reference
from evaluation.rag.multik import aggregate
from evaluation.rag.provenance import code_state
from evaluation.rag.report import build_report, summarize
from evaluation.rag.runner import annotate, ranking_fingerprint, run_benchmark, write_json

ROOT = Path(__file__).resolve().parents[2]


class MultiViewSupplementRanker:
    """Keep Hybrid order intact and add only new canonical Children from View search."""

    def __init__(self, retriever, view_store, reranker, *, candidate_k=20, view_top_k=40, max_supplement=20):
        self.retriever = retriever
        self.pipeline = retriever.pipeline
        self.view_store = view_store
        self.reranker = reranker
        self.candidate_k = candidate_k
        self.view_top_k = view_top_k
        self.max_supplement = max_supplement
        self.sources = {record["chunk_id"]: record for record in retriever.store.records}
        self.details = []

    def _view_candidates(self, query, original_ids):
        vector = self.pipeline.dense.embed([query])[0]
        hits = self.view_store.search(vector, self.view_top_k)
        by_source = {}
        for rank, hit in enumerate(hits, 1):
            source_id = hit["source_child_id"]
            if source_id in by_source:
                by_source[source_id]["matched_view_ids"].append(hit["view_id"])
                continue
            by_source[source_id] = {
                "source_child_id": source_id,
                "view_rank": rank,
                "view_score": hit["dense_score"],
                "matched_view_ids": [hit["view_id"]],
            }

        supplements = []
        for source_id, view in by_source.items():
            if source_id in original_ids:
                continue
            supplements.append({
                **self.sources[source_id],
                "candidate_origin": "multiview_supplement",
                **view,
            })
            if len(supplements) >= self.max_supplement:
                break
        return hits, supplements

    def __call__(self, query, k, strategy):
        if strategy != "hybrid_multiview_supplement_bge_reranker":
            raise ValueError(f"Unsupported experiment strategy: {strategy}")
        original = self.pipeline.rank_candidates(query, self.candidate_k, "hybrid", candidate_k=self.candidate_k)
        original = [dict(item, candidate_origin="hybrid", original_hybrid_rank=rank)
                    for rank, item in enumerate(original, 1)]
        original_ids = {item["chunk_id"] for item in original}
        view_hits, supplements = self._view_candidates(query, original_ids)
        merged = [*original, *supplements]
        reranked = self.reranker.rerank(query, merged)

        self.details.append({
            "query": query,
            "original_hybrid": [
                {"chunk_id": item["chunk_id"], "rank": item["original_hybrid_rank"]}
                for item in original
            ],
            "view_hits": [
                {"view_id": item["view_id"], "source_child_id": item["source_child_id"],
                 "rank": rank, "score": item["dense_score"]}
                for rank, item in enumerate(view_hits, 1)
            ],
            "supplement_child_ids": [item["chunk_id"] for item in supplements],
            "merged_candidate_count": len(merged),
            "final_children": [
                {"chunk_id": item["chunk_id"], "candidate_origin": item["candidate_origin"],
                 "reranker_score": item.get("reranker_score"), "rank": rank}
                for rank, item in enumerate(reranked[:k], 1)
            ],
        })
        return {
            "children": [dict(item, source_block_ids=item["block_ids"]) for item in reranked[:k]],
            "parents": self.pipeline.context_builder.build(reranked, k),
            "candidate_count": len(merged),
            "query_routes": [{"kind": "hybrid", "candidate_count": len(original)},
                             {"kind": "multiview_supplement", "view_count": len(view_hits),
                              "supplement_count": len(supplements)}],
        }


def load_rows(path):
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def metric_line(rows, unit, key, k):
    values = [row["metrics_by_k"][str(k)][unit][key] for row in rows if row["answerable"]]
    return "N/A" if not values else f"{sum(values) / len(values):.4f}"


def comparison_report(output, baseline_rows, supplement_rows, details, config):
    changes = []
    for before, after in zip(baseline_rows, supplement_rows, strict=True):
        if before["question_id"] != after["question_id"]:
            raise ValueError("Comparison questions differ")
        if not before["answerable"]:
            continue
        old = before["metrics_by_k"]["5"]["parent"]
        new = after["metrics_by_k"]["5"]["parent"]
        delta = {key: new[key] - old[key] for key in ("recall", "precision", "mrr", "ndcg")}
        if any(abs(value) > 1e-12 for value in delta.values()):
            changes.append({"question_id": before["question_id"], "question": before["question"],
                            "before": old, "after": new, "delta": delta})
    write_json(output / "rank_changes.json", changes)
    write_json(output / "supplement_details.json", details)

    groups = [
        ("全部", lambda row: True),
        ("中文→英文", lambda row: row["language_pair"] == "zh->en"),
        ("英文→英文", lambda row: row["language_pair"] == "en->en"),
        ("同义表达", lambda row: row["question_type"] == "paraphrase"),
        ("相似技术干扰", lambda row: row["question_type"] == "technique_confusion"),
    ]
    lines = [
        "# 实验二：Multi-View Supplement + BGE Reranker",
        "",
        "固定原始 Hybrid Top 20；Multi-View 只补充原始候选集中没有的 canonical Child，之后统一执行 BGE Reranker，最终取 Top 5。",
        "Multi-View 不参与原始 Hybrid 的重新排序，也不改变生产默认检索路径。",
        "",
        "## 结果对比",
        "",
        "| 方案 | Parent Recall@5 | Parent Recall@10 | Parent MRR@5 | Parent NDCG@5 | P50 ms | P95 ms |",
        "| --- | ---: | ---: | ---: | ---: | ---: | ---: |",
    ]
    baseline_latency = summarize(baseline_rows)["latency_ms"]
    supplement_latency = summarize(supplement_rows)["latency_ms"]
    lines.extend([
        f"| B: Hybrid Top 20 → Reranker | {metric_line(baseline_rows, 'parent', 'recall', 5)} | {metric_line(baseline_rows, 'parent', 'recall', 10)} | {metric_line(baseline_rows, 'parent', 'mrr', 5)} | {metric_line(baseline_rows, 'parent', 'ndcg', 5)} | {baseline_latency['p50']:.2f} | {baseline_latency['p95']:.2f} |",
        f"| C: Hybrid + Supplement → Reranker | {metric_line(supplement_rows, 'parent', 'recall', 5)} | {metric_line(supplement_rows, 'parent', 'recall', 10)} | {metric_line(supplement_rows, 'parent', 'mrr', 5)} | {metric_line(supplement_rows, 'parent', 'ndcg', 5)} | {supplement_latency['p50']:.2f} | {supplement_latency['p95']:.2f} |",
        "",
        "## 分组指标",
        "",
        "| 分组 | 方案 | N | Recall@5 | Recall@10 | MRR@5 | NDCG@5 |",
        "| --- | --- | ---: | ---: | ---: | ---: | ---: |",
    ])
    for label, select in groups:
        for arm, rows in (("B", baseline_rows), ("C", supplement_rows)):
            selected = [row for row in rows if select(row)]
            if not selected:
                continue
            metrics = aggregate(selected, [5, 10])["by_k"]
            lines.append(f"| {label} | {arm} | {sum(row['answerable'] for row in selected)} | "
                         f"{metrics['5']['parent']['recall']:.4f} | {metrics['10']['parent']['recall']:.4f} | "
                         f"{metrics['5']['parent']['mrr']:.4f} | {metrics['5']['parent']['ndcg']:.4f} |")

    improved = [change["question_id"] for change in changes if change["delta"]["recall"] > 0]
    regressed = [change["question_id"] for change in changes if change["delta"]["recall"] < 0]
    supplement_counts = [len(detail["supplement_child_ids"]) for detail in details]
    lines += [
        "",
        "## 变化与边界",
        "",
        f"- 有效候选补充数均值：`{sum(supplement_counts) / len(supplement_counts):.2f}`，最大值：`{max(supplement_counts)}`。",
        f"- Parent Recall@5 改善题：{', '.join(improved) or '无'}。",
        f"- Parent Recall@5 退步题：{', '.join(regressed) or '无'}。",
        f"- 查询错误：`{sum(bool(row['error']) for row in supplement_rows)}`。",
        "- C 的候选内容全部来自原始 Child；View 只用于找到候选，不作为最终证据文本提供给 LLM。",
        "- 详细 View 命中、补充 Child、合并数量和最终排名见 `supplement_details.json`。",
        "- 该实验仍然只评估检索，不代表 LLM 答案质量、Tool 自动选择或拒答能力。",
        "",
        "## 可复现控制变量",
        "",
        f"- 数据集 SHA-256：`{config['dataset_sha256']}`。",
        f"- BGE-M3 Child 索引 SHA-256：`{config['bge_chunks_sha256']}`。",
        f"- 原始 Hybrid 候选数：`{config['candidate_k']}`。",
        f"- View 检索数：`{config['view_top_k']}`；最多补充 Child：`{config['max_supplement']}`。",
        f"- Reranker：`{config['reranker_model']}`。",
    ]
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm")
    parser.add_argument("--dataset", type=Path, default=ROOT / "tests/rag_benchmark/v1/dataset/questions.jsonl")
    parser.add_argument("--bge-index", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/bge_index")
    parser.add_argument("--multiview-run", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-02_security_v1_question_multiview")
    parser.add_argument("--reranker-run", type=Path, default=ROOT / "evaluation_results/reranker_experiment_2026-11-02_v3")
    parser.add_argument("--reranker-model", default="BAAI/bge-reranker-v2-m3")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--view-top-k", type=int, default=40)
    parser.add_argument("--max-supplement", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--ks", type=lambda value: [int(item) for item in value.split(",")], default=[1, 3, 5, 10])
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if args.candidate_k < args.top_k or args.view_top_k <= 0 or args.max_supplement <= 0:
        parser.error("candidate-k must be >= top-k and view limits must be positive")
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    dataset = Dataset(args.dataset)
    dataset.validate_corpus()
    reranker_config = json.loads((args.reranker_run / "B/config.json").read_text(encoding="utf-8"))
    if reranker_config["dataset_sha256"] != dataset.sha256:
        raise ValueError("Reranker baseline uses a different benchmark dataset")
    if reranker_config["candidate_k"] != args.candidate_k or reranker_config["top_k"] != args.top_k:
        raise ValueError("Reranker baseline does not use the requested candidate/final K")
    baseline_rows = load_rows(args.reranker_run / "B/retrieval_results.jsonl")
    if len(baseline_rows) != len(dataset.questions):
        raise ValueError("Reranker baseline question count differs from dataset")

    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    started = time.perf_counter()
    print("Loading frozen BGE-M3 index, Question View index and reranker...", flush=True)
    retriever = load_reference(dataset, args.reference, json.loads((args.reference / "hybrid/config.json").read_text(encoding="utf-8")))
    from app.rag.indexing.snapshot_repository import SnapshotRepository
    from app.rag.indexing.vector_store import FaissVectorStore
    from app.rag.retrieval.reranker import BGEReranker

    bge_store = FaissVectorStore.load(args.bge_index)
    if checksum(args.bge_index / "chunks.jsonl") != reranker_config["bge_chunks_sha256"]:
        raise ValueError("BGE chunks differ from reranker baseline")
    retriever.attach_index(bge_store, retriever.documents, retriever.parents, model_name="BAAI/bge-m3")
    current = json.loads((args.multiview_run / "storage/indexes/current.json").read_text(encoding="utf-8"))
    snapshot = SnapshotRepository(args.multiview_run / "storage").load_generation(current["generation"])
    if snapshot.view_store is None or snapshot.store.records != bge_store.records:
        raise ValueError("Question View generation does not match the frozen BGE Child index")
    reranker = BGEReranker(args.reranker_model)
    ranker = MultiViewSupplementRanker(retriever, snapshot.view_store, reranker,
                                       candidate_k=args.candidate_k, view_top_k=args.view_top_k,
                                       max_supplement=args.max_supplement)

    print(f"Running C: {len(dataset.questions)} queries...", flush=True)
    rows = run_benchmark(dataset, retriever, top_k=args.top_k, strategy="hybrid_multiview_supplement_bge_reranker",
                         evaluation_ks=args.ks, ranker=ranker)
    elapsed = time.perf_counter() - started
    config = {
        "schema_version": 1,
        "metric_contract": METRIC_CONTRACT,
        "annotation_status": "provisional",
        "dataset_sha256": dataset.sha256,
        "dataset": reranker_config["dataset"],
        "bge_chunks_sha256": checksum(args.bge_index / "chunks.jsonl"),
        "candidate_k": args.candidate_k,
        "view_top_k": args.view_top_k,
        "max_supplement": args.max_supplement,
        "top_k": args.top_k,
        "evaluation_ks": args.ks,
        "reranker_model": args.reranker_model,
        "view_generation": current["generation"],
        "view_index_sha256": checksum(args.multiview_run / "storage/indexes" / current["generation"] / "views/faiss.index"),
        "strategy": "hybrid_multiview_supplement_bge_reranker",
        "elapsed_seconds": elapsed,
        "code": code_state(output),
        "ranking_sha256": ranking_fingerprint(rows),
        "baseline_reranker_run": str(args.reranker_run),
        "retrieval": {"strategy": "hybrid_multiview_supplement_bge_reranker", "top_k": args.top_k,
                       "evaluation_ks": args.ks, "candidate_limit_rule": "Hybrid Top 20 plus new canonical View Child",
                       "candidate_k": args.candidate_k},
    }
    folder = output / "C"
    folder.mkdir()
    write_json(folder / "config.json", config)
    (folder / "retrieval_results.jsonl").write_text(
        "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in rows), encoding="utf-8")
    build_report(folder, config, rows)
    comparison_report(output, baseline_rows, rows, ranker.details, config)
    status = {
        "status": "completed" if not any(row["error"] for row in rows) else "completed_with_query_errors",
        "questions": len(rows),
        "query_errors": sum(bool(row["error"]) for row in rows),
        "baseline_rows": len(baseline_rows),
        "elapsed_seconds": elapsed,
        "output": str(output),
    }
    write_json(output / "status.json", status)
    print(json.dumps(status, ensure_ascii=False), flush=True)
    if status["query_errors"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

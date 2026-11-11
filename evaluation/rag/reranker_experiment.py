"""Compare fixed Hybrid Top-20 with BGE reranking on the frozen Security RAG V1 set."""

import argparse
import json
import os
import time
from datetime import datetime
from pathlib import Path

from evaluation.rag.dataset import Dataset, checksum
from evaluation.rag.metrics import METRIC_CONTRACT
from evaluation.rag.model_comparison import load_reference
from evaluation.rag.provenance import code_state
from evaluation.rag.report import build_report
from evaluation.rag.runner import ranking_fingerprint, run_benchmark, write_json

ROOT = Path(__file__).resolve().parents[2]


def load_bge_reference(dataset, baseline, bge_index):
    from app.rag.indexing.vector_store import FaissVectorStore

    config = json.loads((baseline / "hybrid/config.json").read_text(encoding="utf-8"))
    retriever = load_reference(dataset, baseline, config)
    index = FaissVectorStore.load(bge_index)
    if checksum(bge_index / "chunks.jsonl") != config["index"]["chunks_sha256"]:
        raise ValueError("BGE index chunks do not match the frozen benchmark chunks")
    retriever.attach_index(index, retriever.documents, retriever.parents, model_name="BAAI/bge-m3")
    return retriever, config


def original_rank(retriever, query, k, strategy, candidate_k):
    pipeline = retriever.pipeline
    ranked = pipeline.rank_candidates(query, k, strategy, candidate_k=candidate_k)
    return {
        "children": [dict(item, source_block_ids=item["block_ids"]) for item in ranked[:k]],
        "parents": pipeline.context_builder.build(ranked, k),
        "candidate_count": len(ranked),
    }


def reranked_rank(retriever, reranker, query, k, strategy, candidate_k):
    pipeline = retriever.pipeline
    candidates = pipeline.rank_candidates(query, candidate_k, strategy, candidate_k=candidate_k)
    ranked = reranker.rerank(query, candidates)
    return {
        "children": [dict(item, source_block_ids=item["block_ids"]) for item in ranked[:k]],
        "parents": pipeline.context_builder.build(ranked, k),
        "candidate_count": len(candidates),
    }


def metric_line(rows, unit, key, k):
    answerable = [row for row in rows if row["answerable"]]
    value = sum(row["metrics_by_k"][str(k)][unit][key] for row in answerable) / len(answerable)
    return "N/A" if value is None else f"{value:.4f}"


def build_comparison_report(output, baseline_rows, reranked_rows, configs):
    lines = [
        "# BGE Reranker 实验一",
        "",
        "固定同一 BGE-M3 Hybrid 候选池：Top 20 → BGE Reranker → 最终 Top 5。",
        "两组使用相同语料、Chunk、向量索引、BM25Plus、RRF、Ground Truth 和评测口径。",
        "",
        "| 方案 | Parent Recall@5 | Parent Recall@10 | Parent MRR@5 | Parent NDCG@5 |",
        "| --- | ---: | ---: | ---: | ---: |",
    ]
    for label, rows in (("A: Hybrid Top 20", baseline_rows), ("B: Hybrid Top 20 + BGE Reranker", reranked_rows)):
        lines.append("| " + label + " | " + " | ".join(
            [metric_line(rows, "parent", "recall", 5), metric_line(rows, "parent", "recall", 10),
             metric_line(rows, "parent", "mrr", 5), metric_line(rows, "parent", "ndcg", 5)]
        ) + " |")
    lines += [
        "",
        "其中第一列 Recall@5 来自报告的 K=5 结果，第二列 Recall@10 来自 K=10 结果。",
        "不可回答问题不进入普通检索平均；本实验只评估检索，不评估 LLM 答案或拒答。",
        "",
        "## 控制变量",
        "",
        f"- 候选池：每题固定 Hybrid Top `{configs['candidate_k']}`。",
        f"- 最终输出：Top `{configs['top_k']}`。",
        f"- BGE Reranker：`{configs['reranker_model']}`。",
        f"- 数据集 SHA-256：`{configs['dataset_sha256']}`。",
        f"- BGE Chunk 索引：`{configs['bge_chunks_sha256']}`。",
        "- A 不经过 Reranker；B 只改变候选排序，不新增候选，不改变原始证据内容。",
        "",
        "## 典型变化",
        "",
        "详见 `rank_changes.json`，其中记录了每道题的原始 Hybrid 排名、Reranker 排名和证据命中变化。",
    ]
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm")
    parser.add_argument("--dataset", type=Path, default=ROOT / "tests/rag_benchmark/v1/dataset/questions.jsonl")
    parser.add_argument("--bge-index", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc/bge_index")
    parser.add_argument("--reranker-model", default="BAAI/bge-reranker-v2-m3")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--candidate-k", type=int, default=20)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--ks", type=lambda value: [int(k) for k in value.split(",")], default=[1, 3, 5, 10])
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if args.candidate_k < args.top_k or args.top_k <= 0 or any(k <= 0 for k in args.ks):
        parser.error("require candidate-k >= top-k > 0 and positive evaluation K values")
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"

    dataset = Dataset(args.dataset)
    dataset.validate_corpus()
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    status = {
        "created_at": datetime.now().astimezone().isoformat(),
        "dataset_sha256": dataset.sha256,
        "candidate_k": args.candidate_k,
        "top_k": args.top_k,
        "ks": args.ks,
        "reranker_model": args.reranker_model,
        "A": {"status": "not_run"},
        "B": {"status": "not_run"},
    }
    write_json(output / "status.json", status)
    code = code_state(output)
    write_json(output / "code.json", code)

    try:
        retriever, baseline_config = load_bge_reference(dataset, args.baseline, args.bge_index)
        from app.rag.retrieval.reranker import BGEReranker

        started = time.perf_counter()
        reranker = BGEReranker(args.reranker_model)
        reranker_load_seconds = time.perf_counter() - started
    except Exception as error:
        status["A"].update(status="not_run")
        status["B"].update(status="unavailable", reason=f"{type(error).__name__}: {error}")
        write_json(output / "status.json", status)
        print(f"Reranker experiment unavailable: {type(error).__name__}: {error}")
        return

    shared = dict(
        schema_version=1,
        metric_contract=METRIC_CONTRACT,
        dataset_sha256=dataset.sha256,
        bge_chunks_sha256=checksum(args.bge_index / "chunks.jsonl"),
        candidate_k=args.candidate_k,
        top_k=args.top_k,
        evaluation_ks=args.ks,
        reranker_model=args.reranker_model,
        reranker_load_seconds=reranker_load_seconds,
    )
    results = {}
    for label, ranker, strategy in (
        ("A", lambda query, k, route: original_rank(retriever, query, k, "hybrid", args.candidate_k), "hybrid_top20"),
        ("B", lambda query, k, route: reranked_rank(retriever, reranker, query, k, "hybrid", args.candidate_k), "hybrid_top20_bge_reranker"),
    ):
        started = time.perf_counter()
        rows = run_benchmark(dataset, retriever, top_k=args.top_k, strategy=strategy,
                             evaluation_ks=args.ks, ranker=ranker)
        elapsed = time.perf_counter() - started
        folder = output / label
        folder.mkdir()
        config = dict(shared, arm=label, annotation_status="provisional", dataset=baseline_config["dataset"],
                      code=code, strategy=strategy, elapsed_seconds=elapsed,
                      ranking_sha256=ranking_fingerprint(rows), baseline_commit=baseline_config["code"]["commit"],
                      retrieval={"strategy": strategy, "top_k": args.top_k, "evaluation_ks": args.ks,
                                 "candidate_limit_rule": "fixed candidate_k before reranking",
                                 "candidate_k": args.candidate_k})
        write_json(folder / "config.json", config)
        (folder / "retrieval_results.jsonl").write_text(
            "".join(json.dumps(row, ensure_ascii=False, allow_nan=False) + "\n" for row in rows), encoding="utf-8")
        metrics = build_report(folder, config, rows)
        results[label] = (rows, metrics)
        status[label].update(status="completed", metrics_reference=str(folder / "multik_metrics.json"),
                             elapsed_seconds=elapsed)
        write_json(output / "status.json", status)
        print(f"{label} completed: {elapsed:.2f}s")

    baseline_rows, baseline_metrics = results["A"]
    reranked_rows, reranked_metrics = results["B"]
    changes = []
    for before, after in zip(baseline_rows, reranked_rows):
        changes.append({
            "question_id": before["question_id"],
            "question": before["question"],
            "before_children": [{"chunk_id": row["chunk_id"], "rank": row["rank"],
                                 "matched_evidence": row["matched_evidence"]} for row in before["children"]],
            "after_children": [{"chunk_id": row["chunk_id"], "rank": row["rank"],
                                "hybrid_rank": row.get("hybrid_rank"),
                                "reranker_score": row.get("reranker_score"),
                                "matched_evidence": row["matched_evidence"]} for row in after["children"]],
            "before_parent_metrics": before["parent_metrics"],
            "after_parent_metrics": after["parent_metrics"],
        })
    write_json(output / "rank_changes.json", changes)
    build_comparison_report(output, baseline_rows, reranked_rows, shared)
    status["status"] = "completed"
    write_json(output / "status.json", status)
    print(f"Reports: {output}")


if __name__ == "__main__":
    main()

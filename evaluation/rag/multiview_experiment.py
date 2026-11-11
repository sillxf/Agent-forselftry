"""Compare Hybrid and Question Multi-View on unchanged frozen Security Benchmark chunks."""
import argparse
from datetime import datetime
import json
import os
from pathlib import Path
import shutil
import sys
import time

from evaluation.rag.dataset import Dataset, checksum
from evaluation.rag.model_comparison import load_reference
from evaluation.rag.provenance import code_state, model_state
from evaluation.rag.report import build_report, summarize
from evaluation.rag.runner import run_benchmark, ranking_fingerprint, write_json
from evaluation.rag.multik import aggregate

ROOT = Path(__file__).resolve().parents[2]


def compare_rows(baseline, expanded):
    """Keep gains AND regressions, including ranking changes hidden by saturated Recall."""
    changes = []
    for before, after in zip(baseline, expanded, strict=True):
        if before["question_id"] != after["question_id"]:
            raise ValueError("Comparison questions differ")
        if not before["answerable"]:
            continue
        a, b = before["metrics_by_k"]["5"]["parent"], after["metrics_by_k"]["5"]["parent"]
        delta = {metric: b[metric] - a[metric] for metric in ("recall", "precision", "mrr", "ndcg")}
        if any(abs(value) > 1e-12 for value in delta.values()):
            changes.append(dict(question_id=before["question_id"], query=before["question"],
                                before=a, after=b, delta=delta))
    return changes


def comparison_report(output, arms, historical_unchanged):
    changes = compare_rows(arms["hybrid"], arms["multi_view"])
    write_json(output / "changes.json", changes)
    lines = ["# Question Multi-View 检索试验", "", "同一 BGE-M3、语料、原始 Chunk、Ground Truth、Top-K；不生成答案、不评估 Agent 拒答。",
             "新视图仅由文档生成，不读取 Benchmark 问题或答案。人工审核状态未修改；开发集结果不代表泛化能力。", "",
             f"默认 Hybrid 与历史 B 组排名指纹一致：**{historical_unchanged}**。", "",
             "## Parent 证据指标", "", "| 分组 | 模式 | 可答题数 | Recall@5 | Recall@10 | MRR@5 | NDCG@5 | P50 ms | P95 ms |",
             "| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    groups = [("全部", lambda r: True), ("中文→英文", lambda r: r["language_pair"] == "zh->en"),
              ("英文→英文", lambda r: r["language_pair"] == "en->en"),
              ("间接表达", lambda r: r["question_type"] == "paraphrase"),
              ("相似技术干扰", lambda r: r["question_type"] == "technique_confusion")]
    for label, select in groups:
        for mode, rows in arms.items():
            selected = [r for r in rows if select(r)]
            metrics = aggregate(selected, [5, 10])
            latency = summarize(selected)["latency_ms"]
            m5, m10 = metrics["by_k"]["5"]["parent"], metrics["by_k"]["10"]["parent"]
            values = [m5["recall"], m10["recall"], m5["mrr"], m5["ndcg"], latency["p50"], latency["p95"]]
            lines.append(f"| {label} | {mode} | {metrics['answerable']} | " + " | ".join(f"{v:.4f}" for v in values) + " |")
    improved = [r for r in changes if r["delta"]["recall"] > 0]
    regressed = [r for r in changes if r["delta"]["recall"] < 0]
    lines += ["", "## Recall@5 变化", "", f"改善：{', '.join(r['question_id'] for r in improved) or '无'}。",
              f"退步：{', '.join(r['question_id'] for r in regressed) or '无'}。", "",
              "全部排序/Precision/NDCG 变化见 changes.json；每题完整 Top-K 和失败分析见各模式目录。",
              "不能把辅助索引带来的近邻视为可回答证据；不可答题仍只统计无关上下文返回情况。", "",
              "## 成本与边界", "", "生成成本单列于 question_views.manifest.json；查询阶段不调用生成 LLM。",
              "查询耗时不含建库、视图生成和模型加载；两组顺序运行，不是并发负载测试。",
              "本轮只比较一种 Question View；没有同时增加摘要、实体、翻译 Query 或 Reranker。",
              "Multi-View 是显式可选模式，不自动重试，也不替换默认 Hybrid。"]
    before = {r["question_id"]: r for r in arms["hybrid"]}
    after = {r["question_id"]: r for r in arms["multi_view"]}
    lines += ["", "## 变化题目的原文证据排名", "",
              "排名在相同 Top10 中读取；不是生成答案是否正确的判断。", "",
              "| ID | Query | Hybrid 正证据排名 | Multi-View 正证据排名 |", "| --- | --- | --- | --- |"]
    for change in [*improved, *regressed]:
        key = change["question_id"]
        ranks = [", ".join(str(r["rank"]) for r in arm[key]["parents"] if r["matched_evidence"]) or "Top10 未命中"
                 for arm in (before, after)]
        query = change["query"].replace("|", "\\|").replace("\n", " ")
        lines.append(f"| {key} | {query} | {ranks[0]} | {ranks[1]} |")
    a = aggregate(arms["hybrid"], [5, 10])["by_k"]
    b = aggregate(arms["multi_view"], [5, 10])["by_k"]
    delta = (b["5"]["parent"]["recall"] - a["5"]["parent"]["recall"]) * 100
    lines += ["", "## 本轮结论", "", f"全部可答题 Parent Recall@5 变化：{delta:+.2f} 个百分点。",
              "保留 Hybrid 默认，不自动向当前生产知识库发布实验 View。",
              "本轮数据不足以证明 LLM 能可靠地选中受益问题；不将可选接口的实现等同于上线收益。",
              "正确证据在 Top10 中存在、但 Top5 丢失的案例属于排序退步；",
              "可能与问题视图的聚焦方式及嵌套融合有关，不能仅凭此结果断言 Embedding 本身变差。",
              "未为这套题调整权重、扩增 View 或更改标签来改善分数。"]
    (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    return dict(recall_improved=[r["question_id"] for r in improved], recall_regressed=[r["question_id"] for r in regressed],
                historical_hybrid_unchanged=historical_unchanged, parent_recall5_delta_pp=delta,
                production_view_publication=False)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--reference", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-01_security_v1_balanced_minilm")
    parser.add_argument("--bge-run", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-01_security_v1_bge_m3_abc")
    parser.add_argument("--dataset", type=Path, default=ROOT / "tests/rag_benchmark/v1/dataset/questions.jsonl")
    parser.add_argument("--views", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import torch
    import numpy as np
    from app.rag.embedder import get_model
    from app.rag.indexing.pipeline import IndexingPipeline, IndexSnapshot
    from app.rag.indexing.snapshot_repository import SnapshotRepository
    from app.rag.indexing.vector_store import FaissVectorStore
    from app.rag.views import read_views

    torch.manual_seed(0)
    np.random.seed(0)
    dataset = Dataset(args.dataset)
    config = json.loads((args.bge_run / "B/config.json").read_text(encoding="utf-8"))
    if dataset.sha256 != config["dataset"]["sha256"] or checksum(dataset.manifest_path) != config["corpus"]["manifest_sha256"]:
        raise ValueError("Frozen dataset or corpus changed")
    frozen = args.bge_run / "bge_index"
    if checksum(frozen / "faiss.index") != config["index"]["vectors_sha256"]:
        raise ValueError("Frozen BGE index changed")
    manifest_path = args.views.with_suffix(".manifest.json")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    if not manifest["completed"] or manifest["views_sha256"] != checksum(args.views) or manifest["source_chunks_sha256"] != checksum(frozen / "chunks.jsonl"):
        raise ValueError("Incomplete or mismatched frozen views artifact")
    views = read_views(args.views)
    if len(views) != manifest["views"]:
        raise ValueError("View count differs from generation manifest")
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    shutil.copyfile(args.views, output / "question_views.jsonl")
    shutil.copyfile(manifest_path, output / "question_views.manifest.json")
    print("Loading frozen original chunks and BGE-M3...", flush=True)
    reference_config = json.loads((args.reference / "hybrid/config.json").read_text(encoding="utf-8"))
    retriever = load_reference(dataset, args.reference, reference_config)
    original = FaissVectorStore.load(frozen)
    if original.records != retriever.store.records:
        raise ValueError("BGE and reference chunks differ")
    model_name = config["embedding"]["name"]
    model = get_model(model_name)
    embedding = model_state(model_name)
    for key in ("weights_sha256", "tokenizer_sha256"):
        if embedding[key] != config["embedding"][key]:
            raise ValueError("Embedding differs from frozen BGE vectors: " + key)
    retriever.attach_index(original, retriever.documents, retriever.parents, model_name=model_name)
    encode = lambda texts: model.encode(texts, batch_size=4, normalize_embeddings=True, convert_to_numpy=True)
    snapshot = IndexSnapshot(original, retriever.documents, list(retriever.parents.values()))
    started = time.perf_counter()
    snapshot = IndexingPipeline(encode).build_views(snapshot, views, model_name=model_name)
    setup_seconds = time.perf_counter() - started
    repository = SnapshotRepository(output / "storage")
    saved = repository.save(snapshot, config["index"]["signature"])
    retriever.attach_index(original, snapshot.documents, retriever.parents, model_name=model_name,
                           view_store=snapshot.view_store, view_model_name=snapshot.view_model_name)
    repository.publish(saved)
    base = dict(config, embedding=embedding, code=code_state(output),
                started_at=datetime.now().astimezone().isoformat(),
                views=dict(artifact_sha256=checksum(args.views), manifest=manifest,
                           view_index_setup_seconds=setup_seconds, generation=saved.generation,
                           auxiliary_vectors_sha256=checksum(repository.root / saved.generation / "views/faiss.index"),
                           fusion="RRF60(original Dense, best-rank deduplicated View Dense), then RRF60(with BM25)",
                           max_views_per_child=2, query_embedding_calls=1))
    arms = {}
    for mode in ("hybrid", "multi_view"):
        folder = output / mode
        folder.mkdir()
        print(f"Running {mode}: {len(dataset.questions)} queries...", flush=True)
        rows = run_benchmark(dataset, retriever, top_k=config["retrieval"]["top_k"],
                             evaluation_ks=config["retrieval"]["evaluation_ks"], strategy=mode)
        run = dict(base, retrieval=dict(config["retrieval"], strategy=mode), ranking_sha256=ranking_fingerprint(rows))
        write_json(folder / "config.json", run)
        (folder / "retrieval_results.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        build_report(folder, run, rows)
        arms[mode] = rows
    unchanged = ranking_fingerprint(arms["hybrid"]) == config["ranking_sha256"]
    status = comparison_report(output, arms, unchanged)
    status.update(query_errors=sum(bool(r["error"]) for rows in arms.values() for r in rows),
                  questions=len(dataset.questions), views=len(views))
    write_json(output / "status.json", status)
    print(json.dumps(status, ensure_ascii=False), flush=True)
    if status["query_errors"] or not unchanged:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

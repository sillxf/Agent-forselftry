"""Compare Chinese, literal English, multilingual embeddings and dual-query RRF."""
import argparse
import hashlib
import json
import os
import time
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[2]
from app.config import RAG_EMBEDDING_MODEL
from evaluation.rag.dataset import Dataset, checksum
from evaluation.rag.metrics import METRIC_CONTRACT, retrieval_metrics
from evaluation.rag.runner import annotate, derive_qrels, evaluation_units, portable_record, write_json
from evaluation.rag.crosslingual import rank_experiment
from evaluation.rag.provenance import code_state, model_state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--storage-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dataset", type=Path, default=ROOT / "tests/rag_benchmark/dataset/questions.jsonl")
    parser.add_argument("--translations", type=Path, default=ROOT / "tests/rag_benchmark/experiments/crosslingual_queries.json")
    parser.add_argument("--multilingual-model", default=RAG_EMBEDDING_MODEL)
    parser.add_argument("--repetitions", type=int, default=5)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--require-reviewed", action="store_true")
    args = parser.parse_args()
    if args.repetitions < 1:
        parser.error("--repetitions must be positive")
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import numpy as np
    import torch
    from app.rag.embedder import get_model, embed_texts
    from app.rag.indexing.vector_store import FaissVectorStore
    from app.rag.retriever import KnowledgeRetriever
    np.random.seed(0)
    torch.manual_seed(0)
    base = json.loads((args.baseline / "hybrid/config.json").read_text(encoding="utf8"))
    dataset = Dataset(args.dataset, require_reviewed=args.require_reviewed)
    translations = json.loads(args.translations.read_text(encoding="utf8"))
    questions = {q.id: q for q in dataset.questions}
    if args.require_reviewed and (translations["review_status"] != "approved" or not translations["reviewer"]):
        raise ValueError("Translations still need human review")
    if dataset.sha256 != base["dataset"]["sha256"] or checksum(dataset.manifest_path) != base["corpus"]["manifest_sha256"]:
        raise ValueError("Dataset/corpus must match the baseline")
    for entry in translations["questions"]:
        if entry["original_query"] != questions[entry["question_id"]].question:
            raise ValueError("Original query differs from the frozen dataset")
    chunk = base["chunking"]
    retriever = KnowledgeRetriever(knowledge_dir=dataset.documents_dir, storage_dir=args.storage_dir,
        model_name=base["embedding"]["name"], parent_max_tokens=chunk["parent_max_tokens"],
        child_max_tokens=chunk["child_max_tokens"], overlap_tokens=chunk["overlap_tokens"],
        dense_top_k=base["retrieval"]["dense_top_k"], bm25_top_k=base["retrieval"]["bm25_top_k"])
    dataset.validate_corpus()
    dataset.validate_index(retriever)
    records = retriever.store.records
    fingerprint = hashlib.sha256(json.dumps([portable_record(r) for r in records], sort_keys=True,
        ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    if fingerprint != base["index"]["portable_chunks_sha256"]:
        raise ValueError("Chunk bodies/metadata differ from the baseline; do not mix parser runs")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    current_model = model_state(base["embedding"]["name"])
    if any(current_model[key] != base["embedding"][key] for key in ("weights_sha256", "tokenizer_sha256")):
        raise ValueError("Current embedding differs from the baseline")
    started = time.perf_counter()
    get_model(args.multilingual_model)
    model_load_seconds = time.perf_counter() - started
    multilingual_model = model_state(args.multilingual_model)
    texts = [r["search_text"] for r in records]
    started = time.perf_counter()
    cpu_started = time.process_time()
    vectors = embed_texts(texts, args.multilingual_model)
    store = FaissVectorStore(vectors.shape[1])
    store.add(vectors, records)
    store.save(args.output_dir / "multilingual_index")
    build_seconds = time.perf_counter() - started
    build_cpu_seconds = time.process_time() - cpu_started
    token_lengths = [len(get_model(args.multilingual_model).tokenizer.encode(t, truncation=False)) for t in texts]
    k = base["retrieval"]["top_k"]
    units = evaluation_units(retriever)
    rows = []
    for entry in translations["questions"]:
        q = questions[entry["question_id"]]
        qrels = derive_qrels(q, units)
        grades = {e.evidence_id: e.relevance_grade for e in q.relevant_evidence}
        for strategy in ("dense", "bm25", "hybrid"):
            groups = {"A": ([q.question], {}), "B": ([entry["english_query"]], {}),
                      "C": ([q.question], dict(model_name=args.multilingual_model, store=store)),
                      "D": ([q.question, entry["english_query"]], {})}
            results, samples, first_run_ms = {}, {group: [] for group in groups}, {}
            for group, (queries, options) in groups.items():
                started = time.perf_counter()
                results[group] = rank_experiment(retriever, queries, strategy, k, **options)
                first_run_ms[group] = (time.perf_counter() - started) * 1000
            # Warmed repetitions rotate group order to reduce a fixed A->D cache bias.
            for repetition in range(args.repetitions):
                order = list(groups)
                order = order[repetition % 4:] + order[:repetition % 4]
                for group in order:
                    queries, options = groups[group]
                    started = time.perf_counter()
                    result = rank_experiment(retriever, queries, strategy, k, **options)
                    samples[group].append((time.perf_counter() - started) * 1000)
                    if result != results[group]:
                        raise ValueError(f"Non-deterministic ranks: {q.id}/{strategy}/{group}")
            for group, (queries, _) in groups.items():
                ranks = results[group]
                children = annotate(ranks["children"], q, retriever)
                parents = annotate(ranks["parents"], q, retriever, parent=True)
                row = dict(question_id=q.id, original_query=q.question, queries=queries, group=group,
                    strategy=strategy, included_in_benchmark_averages=False, annotation_status="provisional" if dataset.pending_count else "human-reviewed",
                    children=children, parents=parents, expected_evidence=[e.model_dump() for e in q.relevant_evidence],
                    derived_qrels=qrels, candidate_count=ranks["candidate_count"], route_candidates=ranks["route_candidates"],
                    latency_ms=dict(first_run=first_run_ms[group], samples=samples[group], mean=mean(samples[group]),
                                    p50=float(np.median(samples[group])), p95=float(np.percentile(samples[group],95))))
                for name, label in (("children", "child"), ("parents", "parent")):
                    row[label+"_metrics"] = retrieval_metrics([r["matched_evidence"] for r in row[name]], grades, k,
                        ideal_result_grades=list(qrels[name].values()))
                rows.append(row)
    config = dict(metric_contract=METRIC_CONTRACT, code=code_state(args.output_dir), dataset=base["dataset"],
        corpus=base["corpus"], chunking=chunk, frozen_portable_chunks_sha256=fingerprint,
        current_embedding=current_model, multilingual_embedding=multilingual_model,
        index_cost=dict(base_index_setup_seconds=base["index"]["setup_seconds"], base_index_reused_by=["A","B","D"],
            multilingual_model_load_seconds=model_load_seconds, multilingual_embedding_and_index_seconds=build_seconds,
            multilingual_build_cpu_seconds=build_cpu_seconds, multilingual_index_bytes=sum(p.stat().st_size for p in (args.output_dir/"multilingual_index").iterdir()),
            truncated_frozen_chunks=sum(n > multilingual_model["max_sequence_length"] for n in token_lengths),
            frozen_chunks=len(records), multilingual_vectors_sha256=checksum(args.output_dir/"multilingual_index/faiss.index")),
        groups={"A":"Chinese + current embedding", "B":"Fixed English translation + current embedding",
                "C":"Chinese + multilingual embedding, EXACT SAME chunks (model-specific truncation recorded)",
                "D":"Chinese + fixed English routes, current embedding; equal-weight query RRF k0=60"},
        retrieval=base["retrieval"], repetitions=args.repetitions, translation_sha256=checksum(args.translations),
        translations=translations, environment=base["environment"], ranking_stable_across_repetitions=True,
        limits=["Only two development questions; not a holdout or statistical significance test.",
                "Translations are precomputed, not online translation; translation latency/cost is NOT measured.",
                "D doubles candidate retrieval routes; no matched-compute quality claim.",
                "C preserves chunks rather than re-chunking for its tokenizer; long texts may truncate.",
                "BM25 does not embed; C BM25 is a sparse-control repeat of A.",
                "No production model, query policy, RRF or chunk settings are modified."])
    write_json(args.output_dir/"config.json", config)
    (args.output_dir/"results.jsonl").write_text("".join(json.dumps(row,ensure_ascii=False,allow_nan=False)+"\n" for row in rows),encoding="utf8")
    (args.output_dir/"translations.json").write_bytes(args.translations.read_bytes())
    lines=["# 中文跨语言检索对照（候选结果）", "", "原始题目未改变；翻译未混入主 Benchmark；人工审核仍未完成。", ""]
    summary={}
    for unit in ("child", "parent"):
        lines += [f"## {unit.title()} Retrieval Metrics (K={k})", "", f"| Strategy | Group | Recall@{k} | MRR@{k} | NDCG@{k} | Mean ms |", "| --- | --- | ---: | ---: | ---: | ---: |"]
        summary[unit]={}
        for strategy in ("dense", "bm25", "hybrid"):
            summary[unit][strategy]={}
            for group in "ABCD":
                selected=[r for r in rows if r["strategy"]==strategy and r["group"]==group]
                m={key:mean(r[unit+"_metrics"][key] for r in selected) for key in ("recall","mrr","ndcg")}
                m["latency_ms"]=mean(r["latency_ms"]["mean"] for r in selected)
                summary[unit][strategy][group]=m
                lines.append(f"| {strategy} | {group} | "+" | ".join(f"{v:.4f}" for v in m.values())+" |")
        lines.append("")
    lines += ["## 解释边界", "", *["- "+item for item in config["limits"]], "", "## 翻译语义检查", ""]
    lines += [f"- {entry['question_id']}: {entry['semantic_check']}" for entry in translations["questions"]]
    lines += ["", "## 配置决定", "", "结果只能支持下一轮更大样本的翻译/多语言/双路实验，不能证明生产全局最优。", "不自动更换默认模型，不引入 Query Expansion 或 Reranker。", "人工确认答案与翻译后，再用未参与调试的新问题验证收益、成本和语义偏差。", ""]
    write_json(args.output_dir/"summary.json", summary)
    (args.output_dir/"report.md").write_text("\n".join(lines),encoding="utf8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__ == "__main__":
    main()

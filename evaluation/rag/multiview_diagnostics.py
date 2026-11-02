"""Fixed-route attribution for the frozen Multi-View pilot, not a production change or tuning sweep."""
import argparse
import json
import os
from pathlib import Path

from evaluation.rag.dataset import Dataset, checksum
from evaluation.rag.multik import aggregate
from evaluation.rag.provenance import code_state, model_state
from evaluation.rag.runner import derive_qrels, evaluation_units, ranking_fingerprint, run_benchmark, write_json

ROOT = Path(__file__).resolve().parents[2]
MODES = ("original_dense", "view_dense", "bm25", "hybrid", "inner_dense", "view_bm25", "flat_rrf", "multi_view")


def compact(row):
    fields = ("chunk_id", "parent_id", "source", "source_name", "rank", "matched_evidence", "matched_view_ids")
    return {**{key: row[key] for key in ("question_id", "question", "answerable", "language_pair", "question_type", "metrics_by_k", "error")},
            **{unit: [{key: hit[key] for key in fields if key in hit} for hit in row[unit]] for unit in ("children", "parents")}}


def first_rank(ranking, positive, field):
    seen = set()
    for hit in ranking:
        key = hit[field]
        if key in seen:
            continue
        seen.add(key)
        if key in positive:
            return len(seen)
    return None


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run", type=Path, default=ROOT / "evaluation_results/baselines/2026-11-02_security_v1_question_multiview")
    parser.add_argument("--dataset", type=Path, default=ROOT / "tests/rag_benchmark/v1/dataset/questions.jsonl")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--offline", action="store_true")
    args = parser.parse_args()
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import numpy as np
    import torch
    from app.rag.embedder import get_model
    from app.rag.indexing.snapshot_repository import SnapshotRepository
    from app.rag.retriever import KnowledgeRetriever
    from app.rag.retrieval.fusion import RRFFusion

    torch.manual_seed(0)
    np.random.seed(0)
    config = json.loads((args.run / "multi_view/config.json").read_text(encoding="utf-8"))
    dataset = Dataset(args.dataset)
    if dataset.sha256 != config["dataset"]["sha256"] or checksum(dataset.manifest_path) != config["corpus"]["manifest_sha256"]:
        raise ValueError("Frozen dataset or corpus changed")
    repository = SnapshotRepository(args.run / "storage")
    pointer = json.loads((repository.root / "current.json").read_text(encoding="utf-8"))
    generation = repository.root / pointer["generation"]
    if checksum(generation / "faiss.index") != config["index"]["vectors_sha256"] or checksum(generation / "views/faiss.index") != config["views"]["auxiliary_vectors_sha256"]:
        raise ValueError("Frozen vector indexes changed")
    snapshot = repository.load_current(pointer["signature"])
    output = args.output_dir.resolve()
    output.mkdir(parents=True, exist_ok=False)
    print("Loading the SAME frozen embedding and both indexes...", flush=True)
    embedding = model_state(config["embedding"]["name"])
    for key in ("weights_sha256", "tokenizer_sha256"):
        if embedding[key] != config["embedding"][key]:
            raise ValueError("Different embedding: " + key)
    model = get_model(embedding["name"])
    print("Encoding 100 queries individually once; all routes reuse the same vectors...", flush=True)
    vectors = np.asarray([model.encode([q.question], normalize_embeddings=True, convert_to_numpy=True)[0]
                          for q in dataset.questions], dtype="float32")
    np.save(output / "query_vectors.npy", vectors)
    cache = {q.question: vector for q, vector in zip(dataset.questions, vectors)}
    retriever = KnowledgeRetriever(build=False, model_name=embedding["name"],
                                   embedding_fn=lambda texts: np.asarray([cache[text] for text in texts]),
                                   dense_top_k=config["retrieval"]["dense_top_k"], bm25_top_k=config["retrieval"]["bm25_top_k"])
    retriever.attach_index(snapshot.store, snapshot.documents, {p.parent_id: p for p in snapshot.parents},
                           view_store=snapshot.view_store, view_model_name=snapshot.view_model_name)
    dataset.validate_index(retriever)
    depth = max(config["retrieval"]["evaluation_ks"])
    limit = max(retriever.dense_top_k, depth * 4)
    sparse_limit = max(retriever.bm25_top_k, depth * 4)
    sources = {r["chunk_id"]: r for r in snapshot.store.records}
    fusion = RRFFusion()
    units = evaluation_units(retriever)
    routes, diagnostics = {}, []
    represented = {v["source_child_id"] for v in snapshot.view_store.records}
    for question in dataset.questions:
        vector = cache[question.question]
        dense = snapshot.store.search(vector, limit)
        sparse = retriever.pipeline.sparse.retrieve(question.question, sparse_limit)
        raw_views = snapshot.view_store.search(vector, limit * 2)
        all_views = snapshot.view_store.search(vector, len(snapshot.view_store.records))
        candidates = {}
        for hit in raw_views:
            key = hit["source_child_id"]
            if key not in candidates:
                candidates[key] = {**sources[key], "view_score": hit["dense_score"],
                                   "matched_view_types": ["question"], "matched_view_ids": []}
            candidates[key]["matched_view_ids"].append(hit["view_id"])
        views = list(candidates.values())[:limit]
        inner = fusion.fuse([dense, views])
        rankings = dict(original_dense=dense, view_dense=views, bm25=sparse,
                        hybrid=fusion.fuse([dense, sparse]), inner_dense=inner,
                        view_bm25=fusion.fuse([views, sparse]), flat_rrf=fusion.fuse([dense, views, sparse]),
                        multi_view=fusion.fuse([inner, sparse]))
        routes[question.question] = rankings
        qrels = derive_qrels(question, units)
        positive_children, positive_parents = set(qrels["children"]), set(qrels["parents"])
        diagnostics.append(dict(question_id=question.id, query=question.question, answerable=question.answerable,
            positive_child_ids=sorted(positive_children), positive_parent_ids=sorted(positive_parents),
            positive_children_with_views=sorted(positive_children & represented),
            represented_source_count=len(represented),
            full_view_positive_parent_rank=first_rank(all_views, positive_parents, "parent_id"),
            routes={mode: dict(candidates=len(ranks),
                              first_positive_child_rank=first_rank(ranks, positive_children, "chunk_id"),
                              first_positive_parent_rank=first_rank(ranks, positive_parents, "parent_id"),
                              positive_child_ids_in_pool=sorted(positive_children & {r["chunk_id"] for r in ranks}),
                              positive_parent_ids_in_pool=sorted(positive_parents & {r["parent_id"] for r in ranks}))
                    for mode, ranks in rankings.items()},
            top_view_hits=[dict(view_id=v["view_id"], source_child_id=v["source_child_id"], parent_id=v["parent_id"],
                                question=v["search_text"], language=v["language"], score=v["dense_score"],
                                source=sources[v["source_child_id"]]["source_name"],
                                positive_child=v["source_child_id"] in positive_children,
                                positive_parent=v["parent_id"] in positive_parents) for v in raw_views]))
    write_json(output / "route_diagnostics.json", diagnostics)
    results, metrics = {}, {}
    for mode in MODES:
        def ranker(query, k, strategy):
            ranked = routes[query][strategy]
            return dict(children=[dict(r, source_block_ids=r["block_ids"]) for r in ranked[:k]],
                        parents=retriever.pipeline.context_builder.build(ranked, k), candidate_count=len(ranked))
        rows = run_benchmark(dataset, retriever, strategy=mode, top_k=5, evaluation_ks=[1, 3, 5, 10], ranker=ranker)
        results[mode] = rows
        metrics[mode] = dict(overall=aggregate(rows, [1, 3, 5, 10]),
                            zh_to_en=aggregate([r for r in rows if r["language_pair"] == "zh->en"], [5, 10]),
                            errors=sum(bool(r["error"]) for r in rows), ranking_sha256=ranking_fingerprint(rows))
        (output / (mode + ".jsonl")).write_text("".join(json.dumps(compact(r), ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
        print(mode, json.dumps(metrics[mode]["overall"]["by_k"]["5"]["parent"]), flush=True)
    replay = {mode: metrics[mode]["ranking_sha256"] == json.loads((args.run / mode / "config.json").read_text(encoding="utf-8"))["ranking_sha256"]
              for mode in ("hybrid", "multi_view")}
    write_json(output / "metrics.json", metrics)
    write_json(output / "config.json", dict(source_run=str(args.run), dataset_sha256=dataset.sha256,
                original_vectors_sha256=checksum(generation / "faiss.index"), auxiliary_vectors_sha256=checksum(generation / "views/faiss.index"),
                query_vectors_sha256=checksum(output / "query_vectors.npy"), embedding=embedding, code=code_state(output),
                candidate_limit=limit, sparse_limit=sparse_limit, view_raw_limit=limit * 2, rrf_constant=60,
                original_modes_replay=replay, query_latency="Not compared: all diagnostic routes reuse precomputed query vectors"))
    lines = ["# Multi-View 退步归因：固定路线消融", "", "不改模型、语料、View、Ground Truth、候选预算或 RRF 常数；不调权重。",
             "全部方案共用逐题编码一次的原始 Query 向量；本轮不比较查询延迟。所有标签仍保留原审核状态。", "",
             f"原始两组排名指纹复现：{replay}。", "",
             "| 路线 | 全部 Parent R@5 | 全部 Parent R@10 | 全部 MRR@5 | 中文→英文 R@5 |",
             "| --- | ---: | ---: | ---: | ---: |"]
    for mode, item in metrics.items():
        five, ten = item["overall"]["by_k"]["5"]["parent"], item["overall"]["by_k"]["10"]["parent"]
        lines.append(f"| {mode} | {five['recall']:.4f} | {ten['recall']:.4f} | {five['mrr']:.4f} | {item['zh_to_en']['by_k']['5']['parent']['recall']:.4f} |")
    lines += ["", "original_dense=原文 Dense；view_dense=辅助问题 Dense 映射并去重；inner_dense=RRF(原文 Dense, View Dense)。",
              "hybrid=RRF(原文 Dense,BM25)；view_bm25=RRF(View Dense,BM25)。",
              "flat_rrf=RRF(原文 Dense,View Dense,BM25)；multi_view=RRF(inner_dense,BM25)。", "",
              "## 原先 Recall@5 退步的题目", "",
              "| ID | 原文 Dense 正Parent排名 | View 正Parent排名 | Hybrid | 内层融合 | 三路直接融合 | 两层融合 | 正证据Child有View |",
              "| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |"]
    regressed = []
    for i, diagnostic in enumerate(diagnostics):
        if not diagnostic["answerable"] or results["multi_view"][i]["parent_metrics"]["recall"] >= results["hybrid"][i]["parent_metrics"]["recall"]:
            continue
        regressed.append(diagnostic)
        ranks = [str(diagnostic["routes"][m]["first_positive_parent_rank"] or "候选池无")
                 for m in ("original_dense", "view_dense", "hybrid", "inner_dense", "flat_rrf", "multi_view")]
        lines.append(f"| {diagnostic['question_id']} | " + " | ".join(ranks) + f" | {len(diagnostic['positive_children_with_views'])}/{len(diagnostic['positive_child_ids'])} |")
    no_view = [r["question_id"] for r in regressed if not r["positive_children_with_views"]]
    write_json(output / "regressed_cases.json", regressed)
    lines += ["", f"退步题中，没有直接覆盖正证据 Child 的 View：{no_view}。",
              "注意：无正证据 Child View 不等于整个 Parent 无 View；可能存在兄弟 Chunk 的视图。",
              "首个正Parent排名按去重Parent计算，与最终 ParentContextBuilder 一致。",
              "原始 raw View 问题、命中来源、正证据覆盖、各路候选池和排名见 route_diagnostics.json。",
              "消融是开发集机制诊断，不是对 LLM 生成内容做了人工事实审核，也不建立泛化结论。"]
    recall = lambda mode: metrics[mode]["overall"]["by_k"]["5"]["parent"]["recall"]
    lines += ["", "## 可由消融支持的结论", "",
              f"1. 原文 Dense R@5 为 {recall('original_dense'):.2%}，问题 View Dense 为 {recall('view_dense'):.2%}；新增通道明显弱于原通道。",
              f"2. 不加 BM25，单独融合原文和问题 View 后 R@5 已降到 {recall('inner_dense'):.2%}；退步在内层就发生，并非最后一层才导致。",
              f"3. 三路直接 RRF 为 {recall('flat_rrf'):.2%}，比两层融合恢复 {(recall('flat_rrf')-recall('multi_view'))*100:.2f} 个百分点，仍低于原 Hybrid {recall('hybrid'):.2%}；嵌套结构不是唯一原因。",
              f"4. {len(regressed)} 道原先退步题中，有 {len(regressed)-len(no_view)} 道的正证据 Child 至少有一条 View；不能简单归咎于没有生成 View。",
              "5. RRF 按名次投票，不判断原始相似度可信度。弱问题通道也参与等权投票，会使仅在原文排名很高的证据被其他两路都命中的候选超越。",
              "以上是当前固定数据上的路线干预，不是每种因素互相独立的百分比贡献分解。", "",
              "## 问题视图焦点的具体例子", "",
              "这些只是对已冻结文本的对照，不是新增人工审核通过状态。"]
    questions = {q.id: q for q in dataset.questions}
    view_records = snapshot.view_store.records
    for key in ("rag_007", "rag_045", "rag_053"):
        case = next((r for r in regressed if r["question_id"] == key), None)
        if case is None:
            continue
        texts = [r["search_text"] for r in view_records if r["source_child_id"] in case["positive_child_ids"] and r["language"] == "zh"]
        lines += ["", f"### {key}", f"原问题：{questions[key].question}", f"对应正证据 Child 的中文 View：{' / '.join(texts)}"]
    (output / "report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    if not all(replay.values()) or any(item["errors"] for item in metrics.values()):
        raise SystemExit("Replay mismatch or query errors; do not treat diagnostics as the same experiment")


if __name__ == "__main__":
    main()

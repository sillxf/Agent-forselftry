"""Evaluate the frozen corpus with the existing dense/BM25/RRF implementation."""
import argparse
import hashlib
import importlib.metadata
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zipfile import ZipFile, ZipInfo, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.rag.evaluation.dataset import Dataset, checksum
from app.rag.evaluation.report import build_report
from app.rag.evaluation.runner import portable_record, ranking_fingerprint, run_benchmark, write_json


def code_state(output):
    def git(*args):
        return subprocess.check_output(["git", *args], cwd=ROOT, text=True, encoding="utf-8").strip()
    digest = hashlib.sha256()
    paths = [*ROOT.glob("app/**/*.py"), *ROOT.glob("scripts/*.py"), ROOT / "requirements.txt"]
    with ZipFile(output / "source_snapshot.zip", "w", compression=ZIP_DEFLATED) as archive:
        for path in sorted(paths):
            relative = path.relative_to(ROOT).as_posix()
            data = path.read_bytes()
            digest.update(relative.encode())
            digest.update(b"\0" + data + b"\0")
            info = ZipInfo(relative, date_time=(2026, 11, 1, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, data)
    return dict(commit=git("rev-parse", "HEAD"), dirty=bool(git("status", "--porcelain")),
                source_sha256=digest.hexdigest(), snapshot_sha256=checksum(output / "source_snapshot.zip"))


def model_state(name):
    from app.rag.embedder import get_model
    from huggingface_hub import try_to_load_from_cache

    model = get_model(name)
    digest = hashlib.sha256(str(model).encode())
    for key, tensor in sorted(model.state_dict().items()):
        digest.update(key.encode())
        digest.update(tensor.detach().cpu().contiguous().numpy().tobytes())
    tokenizer = model.tokenizer
    tokenizer_definition = json.loads(tokenizer.backend_tokenizer.to_str())
    # encode() changes these transient execution settings; they are not the tokenizer definition.
    tokenizer_definition.pop("padding", None)
    tokenizer_definition.pop("truncation", None)
    repository = name if "/" in name else "sentence-transformers/" + name
    cached_config = try_to_load_from_cache(repository, "config.json") if not Path(name).exists() else None
    revision = Path(cached_config).parent.name if isinstance(cached_config, str) else None
    return dict(name=name, resolved_revision=revision,
                weights_sha256=digest.hexdigest(),
                tokenizer_sha256=hashlib.sha256(json.dumps(tokenizer_definition, sort_keys=True,
                    ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(),
                max_sequence_length=model.max_seq_length, device=str(model.device))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=ROOT / "tests/rag_benchmark/dataset/questions.jsonl")
    parser.add_argument("--retriever", choices=["dense", "bm25", "hybrid", "all"], default="hybrid")
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--model", default="all-MiniLM-L6-v2")
    parser.add_argument("--parent-tokens", type=int, default=1600)
    parser.add_argument("--child-tokens", type=int, default=400)
    parser.add_argument("--overlap-tokens", type=int, default=60)
    parser.add_argument("--dense-top-k", type=int, default=20)
    parser.add_argument("--bm25-top-k", type=int, default=20)
    parser.add_argument("--storage-dir", type=Path, default=ROOT / "app/storage/benchmark")
    parser.add_argument("--output-dir", type=Path)
    parser.add_argument("--offline", action="store_true", help="Require previously cached model artifacts")
    parser.add_argument("--require-reviewed", action="store_true", help="Refuse provisional human-unreviewed labels")
    args = parser.parse_args()
    if args.top_k <= 0:
        parser.error("--top-k must be positive")
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = "1"
        os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ["TOKENIZERS_PARALLELISM"] = "false"
    import numpy as np
    import torch
    from app.rag.retriever import KnowledgeRetriever
    from app.rag.embedder import get_model

    torch.manual_seed(0)
    np.random.seed(0)
    dataset = Dataset(args.dataset, require_reviewed=args.require_reviewed)
    dataset.validate_corpus()
    if dataset.pending_count:
        print(f"PROVISIONAL: {dataset.pending_count} questions still need human review.", flush=True)
    started = time.perf_counter()
    retriever = KnowledgeRetriever(knowledge_dir=dataset.documents_dir, storage_dir=args.storage_dir,
        model_name=args.model, parent_max_tokens=args.parent_tokens, child_max_tokens=args.child_tokens,
        overlap_tokens=args.overlap_tokens, dense_top_k=args.dense_top_k, bm25_top_k=args.bm25_top_k)
    setup_seconds = time.perf_counter() - started
    dataset.validate_index(retriever)
    now = datetime.now(timezone(timedelta(hours=8)))
    output = args.output_dir or ROOT / "evaluation_results" / now.strftime("%Y-%m-%d_%H%M%S_%f")
    output.mkdir(parents=True, exist_ok=False)
    index_pointer = args.storage_dir / "indexes/current.json"
    pointer = json.loads(index_pointer.read_text(encoding="utf-8"))
    index_dir = index_pointer.parent / pointer["generation"]
    base = dict(
        schema_version=1, started_at=now.isoformat(), code=code_state(output),
        annotation_status="provisional" if dataset.pending_count else "human-reviewed",
        dataset=dict(version=dataset.metadata["version"], sha256=dataset.sha256,
                     metadata_sha256=checksum(dataset.metadata_path), path=str(dataset.path)),
        corpus=dict(version=dataset.manifest["version"], manifest_sha256=checksum(dataset.manifest_path),
                    documents=dataset.manifest["documents"]),
        embedding=model_state(args.model),
        index=dict(generation=pointer["generation"], pipeline_version=retriever.INDEX_VERSION,
                   signature=pointer["signature"], ocr_enabled=retriever.parser.ocr_enabled,
                   chunks_sha256=checksum(index_dir / "chunks.jsonl"),
                   portable_chunks_sha256=hashlib.sha256(json.dumps([portable_record(r) for r in retriever.store.records],
                       sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest(), vectors_sha256=checksum(index_dir / "faiss.index"),
                   setup_seconds=setup_seconds, size_bytes=sum(p.stat().st_size for p in index_dir.iterdir() if p.is_file()),
                   documents=len(retriever.documents), parents=len(retriever.parents), children=len(retriever.store.records)),
        chunking=dict(parent_max_tokens=args.parent_tokens, child_max_tokens=args.child_tokens,
                      effective_child_max_tokens=min(args.child_tokens, get_model(args.model).max_seq_length -
                                                     get_model(args.model).tokenizer.num_special_tokens_to_add(pair=False)),
                      overlap_tokens=args.overlap_tokens),
        environment=dict(python=sys.version, platform=platform.platform(), machine=platform.machine(),
                         torch_threads=torch.get_num_threads(), seed=0,
                         dependencies={d.metadata["Name"]: d.version for d in sorted(importlib.metadata.distributions(), key=lambda d: d.metadata["Name"].lower())}),
    )
    strategies = ["dense", "bm25", "hybrid"] if args.retriever == "all" else [args.retriever]
    comparison, had_errors = {}, False
    for strategy in strategies:
        target = output / strategy if args.retriever == "all" else output
        if target != output:
            target.mkdir()
        config = dict(base, retrieval=dict(strategy=strategy, top_k=args.top_k, dense_top_k=args.dense_top_k,
                bm25_top_k=args.bm25_top_k, candidate_limit_rule="max(configured_top_k, K*4)",
                rrf_rank_constant=60, bm25=dict(type="BM25Plus", k1=retriever._bm25.k1, b=retriever._bm25.b,
                                             delta=retriever._bm25.delta), reranker=False))
        rows = run_benchmark(dataset, retriever, top_k=args.top_k, strategy=strategy)
        config["ranking_sha256"] = ranking_fingerprint(rows)
        write_json(target / "config.json", config)
        (target / "retrieval_results.jsonl").write_text("".join(json.dumps(r, ensure_ascii=False, allow_nan=False) + "\n" for r in rows), encoding="utf-8")
        metrics = build_report(target, config, rows)
        comparison[strategy] = metrics["overall"]
        had_errors |= metrics["overall"]["errors"] > 0
        print(strategy, json.dumps(metrics["overall"]["child"]), flush=True)
    if args.retriever == "all":
        write_json(output / "comparison.json", comparison)
        lines = ["# Candidate retrieval comparison", "",
                 f"Annotation status: **{base['annotation_status']}**. Do not treat pending labels as human-reviewed acceptance.",
                 "All strategies share the same corpus, index, embedding and chunking configuration.", "",
                 "| Strategy | Child Recall@K | Child Precision@K | Child MRR@K | Child NDCG@K | Parent Recall@K |",
                 "| --- | ---: | ---: | ---: | ---: | ---: |"]
        for strategy, summary in comparison.items():
            child = summary["child"]
            values = [child[key] for key in ("recall", "precision", "mrr", "ndcg")] + [summary["parent"]["recall"]]
            lines.append(f"| {strategy} | " + " | ".join(f"{value:.4f}" if value is not None else "N/A" for value in values) + " |")
        lines += ["", f"K={args.top_k}. Recall is unique evidence coverage within K child or K unique-parent ranks.",
                  "Novelty-aware precision/NDCG conventions are documented in each report. Unanswerable cases are excluded.",
                  "Only rank/metric comparisons are meaningful here; sequential strategy order affects cache/latency measurements.",
                  "The exact implementation is archived in source_snapshot.zip; config files record its hash."]
        (output / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"Reports: {output.resolve()}")
    if had_errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()

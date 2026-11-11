"""Subprocess boundary: import the requested code revision, never both app versions."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import statistics
import sys
import time


def digest(value):
    return hashlib.sha256(json.dumps(value, ensure_ascii=False, sort_keys=True,
                                    separators=(",", ":")).encode()).hexdigest()


def canonical_result(result, documents):
    document = documents[result["document_id"]]
    return {"source": document.filename, "source_checksum": document.checksum,
            "content": result["content"], "page_start": result.get("page_start"),
            "page_end": result.get("page_end"),
            "source_block_ids": result.get("source_block_ids", result.get("block_ids", []))}


def exercise(retriever, options, query):
    """Fault injection is confined to this disposable storage, using real index/model I/O."""
    from unittest.mock import patch
    from app.rag.retriever import KnowledgeRetriever
    original = retriever._generation_id
    started = time.perf_counter()
    retriever.build_index()
    checks = {"warm_rebuild": {"seconds": time.perf_counter() - started,
                               "cache": retriever.last_build_metrics}}
    warm = retriever._generation_id
    pointer = retriever.repository.root / "current.json"
    before = pointer.read_bytes()
    with patch.object(retriever, "_assemble_snapshot", side_effect=RuntimeError("acceptance injected build failure")):
        try:
            retriever.build_index()
        except RuntimeError:
            pass
    checks["failed_build_keeps_pointer"] = pointer.read_bytes() == before
    checks["failed_job_persisted"] = retriever.registry.list_jobs()[0]["status"] == "failed"
    restarted = KnowledgeRetriever(**options)
    checks["restart_keeps_published_generation"] = restarted._generation_id == warm
    # Damage a real generation asset, then simulate the parser being unavailable on restart.
    asset = retriever.repository.root / warm / "faiss.index"
    asset.write_bytes(b"acceptance injected corruption")
    fallback = KnowledgeRetriever(build=False, **options)
    with patch.object(fallback, "_assemble_snapshot", side_effect=RuntimeError("acceptance parser offline")):
        fallback.search(query, 2)
    checks["corrupt_current_recovers_previous"] = fallback._generation_id == original
    fallback.build_index()
    intact = fallback._generation_id
    document = fallback.documents[0]
    # Use a complete sparse ranking so absence isn't mistaken for a Top-K miss.
    probe = next(p.content for p in fallback.parents.values() if p.document_id == document.document_id)
    def visible():
        rows = fallback.search_rankings(probe[:500], max(1, len(fallback.parents)), "bm25")["parents"]
        return any(row["document_id"] == document.document_id for row in rows)
    checks["document_visible_before_delete"] = visible()
    fallback.lifecycle.delete(document.document_id)
    checks["delete_immediate"] = not visible()
    fallback.rollback_generation(original)
    checks["rollback_preserves_tombstone"] = not visible()
    cold = KnowledgeRetriever(**options)
    checks["restart_preserves_rollback_and_tombstone"] = (cold._generation_id == original and
        all(row["document_id"] != document.document_id for row in cold.search_rankings(probe[:500],
            max(1, len(cold.parents)), "bm25")["parents"]))
    fallback.lifecycle.restore(document.document_id)
    checks["restore_visible"] = visible()
    fallback.lifecycle.set_validity(document.document_id, expires_at="2000-01-01T00:00:00+00:00")
    checks["expiration_immediate"] = not visible()
    fallback.lifecycle.set_validity(document.document_id, effective_at="2100-01-01T00:00:00+00:00")
    checks["future_effective_hidden"] = not visible()
    fallback.lifecycle.set_validity(document.document_id)
    checks["validity_reset_visible"] = visible()
    fallback.rollback_generation(intact)
    return checks


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--code-root", type=Path, required=True)
    parser.add_argument("--storage-dir", type=Path, required=True)
    parser.add_argument("--knowledge-dir", type=Path, required=True)
    parser.add_argument("--dataset", type=Path)
    parser.add_argument("--queries", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", required=True)
    parser.add_argument("--top-k", type=int, default=5)
    parser.add_argument("--exercise", action="store_true")
    parser.add_argument("--load-only", action="store_true")
    args = parser.parse_args()
    sys.path.insert(0, str(args.code_root.resolve()))
    os.environ.update(HF_HUB_OFFLINE="1", TRANSFORMERS_OFFLINE="1", TOKENIZERS_PARALLELISM="false",
                      RAG_RETRIEVAL_STRATEGY="hybrid")
    import numpy as np
    import torch
    from app.rag.retriever import KnowledgeRetriever
    np.random.seed(0)
    torch.manual_seed(0)
    options = dict(knowledge_dir=args.knowledge_dir, storage_dir=args.storage_dir, model_name=args.model,
                   parent_max_tokens=1600, child_max_tokens=400, overlap_tokens=60,
                   dense_top_k=20, bm25_top_k=20)
    started = time.perf_counter()
    retriever = KnowledgeRetriever(build=False, **options)
    if args.load_only:
        retriever.pipeline
    else:
        retriever.build_index()
    setup = time.perf_counter() - started
    documents = {d.document_id: d for d in retriever.documents}
    rows = []
    pending = None
    if args.dataset:
        from evaluation.rag.dataset import Dataset
        from evaluation.rag.runner import run_benchmark
        dataset = Dataset(args.dataset)
        pending = dataset.pending_count
        rows = run_benchmark(dataset, retriever, top_k=args.top_k, evaluation_ks=[1, 3, 5])
        queries = [{"id": row["question_id"], "query": row["question"]} for row in rows]
    else:
        queries = json.loads(args.queries.read_text(encoding="utf-8"))
    served, times = [], []
    for item in queries:
        start = time.perf_counter()
        result = retriever.search(item["query"], args.top_k)
        times.append((time.perf_counter() - start) * 1000)
        served.append({"id": item["id"], "results": [canonical_result(r, documents) for r in result]})
    units = {"children": sorted((canonical_result(r, documents) for r in retriever.store.records), key=digest),
             "parents": sorted(({"source": documents[p.document_id].filename,
                                  "source_checksum": documents[p.document_id].checksum,
                                  "content": p.content} for p in retriever.parents.values()), key=digest)}
    result = {"index_format": retriever.INDEX_VERSION, "setup_seconds": setup,
              "storage_bytes": sum(p.stat().st_size for p in args.storage_dir.rglob("*") if p.is_file()),
              "counts": dict(documents=len(documents), parents=len(retriever.parents), children=len(retriever.store.records)),
              "cache": getattr(retriever, "last_build_metrics", {}), "pending_questions": pending,
              "latency_ms": {"median": statistics.median(times), "p95": sorted(times)[max(0, int(len(times)*.95)-1)]},
              "units_fingerprint": digest(units), "served": served, "benchmark": rows,
              "generation": json.loads((args.storage_dir / "indexes/current.json").read_text())["generation"]}
    # Save the baseline observations before fault injection, even if a drill fails.
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")
    if args.exercise:
        result["recovery"] = exercise(retriever, options, queries[0]["query"])
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False), encoding="utf-8")


if __name__ == "__main__":
    main()

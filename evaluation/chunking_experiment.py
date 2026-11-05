"""Bounded chunk-size experiment over the frozen Security V1 benchmark.

Question: does the product default (child 400 / parent 1600 / overlap 60) retrieve
as well as nearby alternatives? Runs the CURRENT product chunkers, BGE-M3 Dense,
BM25 and RRF through RetrievalPipeline. No reranker, no LLM, no paid calls.

Stop rule (decided before running): keep the default unless an alternative beats it
on the development split by at least 1.0 point in BOTH Parent Recall@5 and Parent
MRR@5, and does not lose on the holdout split. The holdout split is reported but is
never used to pick a setting.

Usage (repository root, after `pip install -e .`):
    python -m evaluation.chunking_experiment --output evaluation/results/chunking-<date>
Add --offline once BGE-M3 is cached; --limit N runs a quick N-question link check.
"""

import argparse
import hashlib
import json
import os
import platform
import sys
import time
from pathlib import Path
from statistics import mean

ROOT = Path(__file__).resolve().parents[1]
BENCHMARK = ROOT / "evaluation/benchmark/security-v1"
DEFAULT = (400, 1600, 60)
CONFIGS = {
    "child200": (200, 1600, 30),
    "child400-default": DEFAULT,
    "child800": (800, 1600, 120),
}
KS = (1, 3, 5, 10)


def normalize(text):
    return " ".join(text.casefold().split())


def holdout(question):
    """20% of query families, by stable hash. Variants of one question stay together."""
    family = question["query_family"]
    return int(hashlib.sha256(("holdout-v1:" + family).encode()).hexdigest(), 16) % 5 == 0


def load_benchmark():
    manifest = json.loads((BENCHMARK / "manifest.json").read_text(encoding="utf-8"))
    for entry in manifest["documents"]:
        actual = hashlib.sha256((BENCHMARK / "documents" / entry["file"]).read_bytes())
        if actual.hexdigest() != entry["sha256"]:
            raise ValueError(f"Frozen benchmark document changed: {entry['file']}")
    questions = [
        json.loads(line)
        for line in (BENCHMARK / "dataset/questions.jsonl").read_text(encoding="utf-8").splitlines()
        if line.strip()
    ]
    english = json.loads((BENCHMARK / "english_queries.json").read_text(encoding="utf-8"))
    return manifest, questions, english


def matched(unit_blocks, content, document_name, question):
    """Same rule as the historical runner: block identity AND quote inside the unit."""
    body = normalize(content)
    found = []
    for evidence in question["relevant_evidence"]:
        for anchor in [evidence, *evidence.get("alternatives", [])]:
            if (
                anchor["source"] == document_name
                and unit_blocks & set(anchor["source_block_ids"])
                and normalize(anchor["text_quote"]) in body
            ):
                found.append(evidence["evidence_id"])
                break
    return found


def parse_corpus(cache_dir):
    """Parse each frozen document once; parsing does not depend on chunk sizes."""
    from app.ingestion.docling_parser import DoclingParser
    from app.ingestion.processing.cross_page_merger import CrossPageMerger
    from app.ingestion.processing.structure_recovery import StructureRecovery
    from app.knowledge.models import ParsedDocument

    cache_dir.mkdir(parents=True, exist_ok=True)
    parser = DoclingParser(ocr_enabled=True)
    parsed = []
    for path in sorted((BENCHMARK / "documents").iterdir()):
        cached = cache_dir / (path.name + ".json")
        if cached.exists():
            item = ParsedDocument.model_validate_json(cached.read_text(encoding="utf-8"))
        else:
            item = parser.parse(path)
            item.structured_data = {}
            cached.write_text(item.model_dump_json(), encoding="utf-8")
        item.blocks = StructureRecovery().recover(CrossPageMerger().merge(item.blocks))
        parsed.append(item)
    return parsed


def build_pipeline(parsed, provider, child, parent, overlap, embed_cache):
    import numpy as np

    from app.ingestion.chunking.child_chunker import ChildChunker
    from app.ingestion.chunking.parent_chunker import ParentChunker
    from app.retrieval.pipeline import RetrievalPipeline
    from app.storage.vector_store import FaissVectorStore

    tokenizer, limit = provider.tokenizer_and_limit()
    child = min(child, limit - tokenizer.num_special_tokens_to_add(pair=False))
    parents, children = [], []
    for item in parsed:
        for p in ParentChunker(tokenizer, parent).split(item.blocks, item.document):
            parents.append(p)
            children.extend(
                ChildChunker(tokenizer, child, overlap).split(
                    p, item.document.filename, item.document.file_type
                )
            )
    records = [c.model_dump(mode="json") for c in children]
    started = time.perf_counter()
    texts, encode = [r["search_text"] for r in records], embed_cache("document")
    # Small batches are persisted as they finish, so an interrupted run resumes.
    vectors = np.concatenate(
        [encode(texts[i : i + 16]) for i in range(0, len(texts), 16)]
    )
    encode_seconds = time.perf_counter() - started
    store = FaissVectorStore(vectors.shape[1])
    store.add(vectors, records)
    pipeline = RetrievalPipeline.from_index(
        store, {p.parent_id: p for p in parents}, embed=embed_cache("query")
    )
    names = {item.document.document_id: item.document.filename for item in parsed}
    stats = dict(
        parents=len(parents),
        children=len(children),
        effective_child_tokens=child,
        encode_seconds=round(encode_seconds, 1),
    )
    return pipeline, names, stats


def ideal_grades(question, units):
    grades = {e["evidence_id"]: e["relevance_grade"] for e in question["relevant_evidence"]}
    output = []
    for blocks, content, name in units:
        found = matched(blocks, content, name, question)
        if found:
            output.append(max(grades[f] for f in found))
    return output


def evaluate(pipeline, names, questions, english, use_english):
    from evaluation.metrics import retrieval_metrics

    parent_units = [
        (
            {k for b in p.blocks for k in (b.source_block_ids or [b.block_id])},
            p.content,
            names[p.document_id],
        )
        for p in pipeline.context_builder.parents.values()
    ]
    rows = []
    for q in questions:
        extra = []
        if use_english and english[q["id"]]["english"] != q["question"]:
            extra = [english[q["id"]]["english"]]
        started = time.perf_counter()
        ranked = pipeline.rank_candidates(q["question"], max(KS), "hybrid", extra_queries=extra)
        latency = (time.perf_counter() - started) * 1000
        parents = pipeline.context_builder.build(ranked, max(KS))
        grades = {e["evidence_id"]: e["relevance_grade"] for e in q["relevant_evidence"]}
        hits = [
            matched(
                {
                    k
                    for b in pipeline.context_builder.parents[r["parent_id"]].blocks
                    for k in (b.source_block_ids or [b.block_id])
                },
                r["content"],
                names[r["document_id"]],
                q,
            )
            for r in parents
        ]
        row = dict(id=q["id"], holdout=holdout(q), answerable=q["answerable"], latency_ms=latency)
        if q["answerable"]:
            required = {e["evidence_id"] for e in q["relevant_evidence"] if e["relevance_grade"]}
            locatable = {f for unit in parent_units for f in matched(*unit, q)}
            if not required <= locatable:
                # The parser did not reproduce the labelled text (e.g. a sentence split
                # by a misread heading). Report it; never score a fact that cannot match.
                row["unresolved_evidence"] = sorted(required - locatable)
            else:
                ideal = ideal_grades(q, parent_units)
                for k in KS:
                    row[f"k{k}"] = retrieval_metrics(hits, grades, k, ideal_result_grades=ideal)
        rows.append(row)
    return rows


def summarize(rows):
    def side(selected):
        answerable = [r for r in selected if r["answerable"] and "k5" in r]
        out = dict(
            questions=len(selected),
            scored_answerable=len(answerable),
            unresolved=[r["id"] for r in selected if "unresolved_evidence" in r],
        )
        for k in KS:
            for metric in ("recall", "mrr", "ndcg"):
                out[f"{metric}@{k}"] = round(
                    100 * mean(r[f"k{k}"][metric] for r in answerable), 2
                ) if answerable else None
        out["p50_ms"] = round(sorted(r["latency_ms"] for r in selected)[len(selected) // 2], 1)
        return out

    return dict(
        development=side([r for r in rows if not r["holdout"]]),
        holdout=side([r for r in rows if r["holdout"]]),
    )


def decide(summary):
    base = summary["child400-default"]
    winners = []
    for name, value in summary.items():
        if name == "child400-default":
            continue
        dev, hold = value["development"], value["holdout"]
        if (
            dev["recall@5"] - base["development"]["recall@5"] >= 1.0
            and dev["mrr@5"] - base["development"]["mrr@5"] >= 1.0
            and hold["recall@5"] >= base["holdout"]["recall@5"]
            and hold["mrr@5"] >= base["holdout"]["mrr@5"]
        ):
            winners.append(name)
    return winners


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--offline", action="store_true")
    parser.add_argument("--limit", type=int, help="Link check on the first N questions only")
    parser.add_argument("--configs", default=",".join(CONFIGS))
    args = parser.parse_args()
    if args.offline:
        os.environ["HF_HUB_OFFLINE"] = os.environ["TRANSFORMERS_OFFLINE"] = "1"
    os.environ.setdefault("TOKENIZERS_PARALLELISM", "false")
    from app.core.config import RAG_EMBEDDING_MODEL
    from app.models.embedding.provider import EmbeddingProvider
    from app.models.pool import ModelPool

    # Reusing an output directory resumes from its parse and embedding caches.
    args.output.mkdir(parents=True, exist_ok=True)
    manifest, questions, english = load_benchmark()
    if args.limit:
        questions = questions[: args.limit]
    provider = EmbeddingProvider(
        dict(kind="embedding", provider="sentence_transformers", model=RAG_EMBEDDING_MODEL),
        ModelPool(1),
    )
    started = time.perf_counter()
    parsed = parse_corpus(args.output / "parsed")
    parse_seconds = time.perf_counter() - started
    from app.indexing.embedding_cache import CachedEmbedder

    def embed_cache(kind):
        # Content-addressed vectors: an interrupted run resumes without re-encoding.
        encode = provider.embed_documents if kind == "document" else provider.embed_query
        return CachedEmbedder(
            encode,
            args.output / "embedding_cache",
            {"model": RAG_EMBEDDING_MODEL, "kind": kind},
        )

    summary, details = {}, {}
    for name in args.configs.split(","):
        pipeline, names, stats = build_pipeline(
            parsed, provider, *CONFIGS[name], embed_cache
        )
        for routes, use_english in (("original", False), ("original+english", True)):
            key = name if routes == "original" else name + "+english"
            rows = evaluate(pipeline, names, questions, english, use_english)
            summary[key] = dict(summarize(rows), index=stats)
            details[key] = rows
            print(key, json.dumps(summary[key]["development"]), flush=True)
    base_only = {k: v for k, v in summary.items() if not k.endswith("+english")}
    result = dict(
        benchmark=dict(
            version=manifest["version"],
            questions_sha256=hashlib.sha256(
                (BENCHMARK / "dataset/questions.jsonl").read_bytes()
            ).hexdigest(),
            questions=len(questions),
            limited=bool(args.limit),
        ),
        embedding=RAG_EMBEDDING_MODEL,
        configs={k: dict(child=v[0], parent=v[1], overlap=v[2]) for k, v in CONFIGS.items()},
        stop_rule="Switch only if dev Recall@5 and MRR@5 both improve >=1.0pt and holdout does not drop",
        switch_to=None if args.limit or "child400-default" not in base_only else decide(base_only),
        parse_seconds=round(parse_seconds, 1),
        environment=dict(python=sys.version.split()[0], platform=platform.platform()),
        summary=summary,
    )
    (args.output / "summary.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    (args.output / "per_question.json").write_text(
        json.dumps(details, ensure_ascii=False), encoding="utf-8"
    )
    print(json.dumps({k: result[k] for k in ("switch_to", "parse_seconds")}, ensure_ascii=False))


if __name__ == "__main__":
    main()

"""Explicit offline generation/build commands; normal queries never invoke a generator."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
import os
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import LLM_API_KEY, LLM_BASE_URL, LLM_MODEL
from app.llm.client import LLMClient
from app.rag.views import PROMPT_VERSION, generate_question_views, read_views


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    generate = commands.add_parser("generate", help="Generate from source chunks only; no benchmark input")
    generate.add_argument("--chunks", type=Path, required=True)
    generate.add_argument("--output", type=Path, required=True)
    generate.add_argument("--batch-size", type=int, default=8)
    generate.add_argument("--workers", type=int, default=1)
    generate.add_argument("--max-batches", type=int, default=100, help="Preflight request-count budget; no partial paid run")
    generate.add_argument("--model", default=os.getenv("RAG_VIEW_LLM_MODEL", LLM_MODEL))
    generate.add_argument("--base-url", default=os.getenv("RAG_VIEW_LLM_BASE_URL", LLM_BASE_URL))
    build = commands.add_parser("build", help="Add frozen views to the active production generation")
    build.add_argument("--views", type=Path, required=True)
    build.add_argument("--storage-dir", type=Path)
    build.add_argument("--knowledge-dir", type=Path)
    args = parser.parse_args()
    if args.command == "build":
        from app.rag.retriever import KnowledgeRetriever
        manifest = json.loads(args.views.with_suffix(".manifest.json").read_text(encoding="utf-8"))
        if not manifest["completed"] or manifest["views_sha256"] != hashlib.sha256(args.views.read_bytes()).hexdigest():
            raise ValueError("Incomplete or changed question views artifact")
        retriever = KnowledgeRetriever(build=False, storage_dir=args.storage_dir, knowledge_dir=args.knowledge_dir)
        retriever.build_view_index(read_views(args.views))
        print("Published Question View generation; Hybrid remains the default.")
        return
    if args.batch_size <= 0 or not 1 <= args.workers <= 4 or args.max_batches <= 0:
        parser.error("batch-size/max-batches must be positive and workers must be between 1 and 4")
    records = [json.loads(line) for line in args.chunks.read_text(encoding="utf-8").splitlines() if line.strip()]
    batches = [records[i:i + args.batch_size] for i in range(0, len(records), args.batch_size)]
    if len(batches) > args.max_batches:
        parser.error(f"Generation needs {len(batches)} requests, exceeding --max-batches={args.max_batches}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    llm = LLMClient(os.getenv("RAG_VIEW_LLM_API_KEY", LLM_API_KEY), args.base_url, args.model)
    # Explicit offline command only. Bound request duration; errors remain errors, no substitutes.
    llm._client = llm._get_client().with_options(timeout=180, max_retries=0)
    manifest = dict(source_chunks_sha256=hashlib.sha256(args.chunks.read_bytes()).hexdigest(),
                    generator_model=llm.model, prompt_version=PROMPT_VERSION, batch_size=args.batch_size,
                    source_chunks=len(records), completed=False)
    manifest_path = args.output.with_suffix(".manifest.json")
    started = time.perf_counter()
    count = 0
    covered = set()
    with args.output.open("x", encoding="utf-8") as output:
        manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            # Only one worker wave is submitted, bounding paid work after failure.
            for start in range(0, len(batches), args.workers):
                futures = [pool.submit(generate_question_views, batch, llm)
                           for batch in batches[start:start + args.workers]]
                try:
                    for offset, future in enumerate(futures, 1):
                        views = future.result()
                        output.write("".join(view.model_dump_json() + "\n" for view in views))
                        output.flush()
                        count += len(views)
                        covered.update(view.source_child_id for view in views)
                        print(f"Batch {start + offset}/{len(batches)}; {count} question views", flush=True)
                except Exception:
                    for future in futures:
                        future.cancel()
                    raise
    manifest.update(completed=True, views=count, covered_source_chunks=len(covered),
                    skipped_source_chunks=len(records) - len(covered), generation_seconds=time.perf_counter() - started,
                    views_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest())
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

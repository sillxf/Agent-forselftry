"""Explicit offline generation/build commands; normal queries never invoke a generator."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import json
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
    if args.batch_size <= 0 or args.workers <= 0:
        parser.error("batch-size and workers must be positive")
    records = [json.loads(line) for line in args.chunks.read_text(encoding="utf-8").splitlines() if line.strip()]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    llm = LLMClient(LLM_API_KEY, LLM_BASE_URL, LLM_MODEL)
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
        batches = [records[i:i + args.batch_size] for i in range(0, len(records), args.batch_size)]
        with ThreadPoolExecutor(max_workers=args.workers) as pool:
            for index, views in enumerate(pool.map(lambda batch: generate_question_views(batch, llm), batches), 1):
                output.write("".join(view.model_dump_json() + "\n" for view in views))
                output.flush()
                count += len(views)
                covered.update(view.source_child_id for view in views)
                print(f"Batch {index}/{len(batches)}; {count} question views", flush=True)
    manifest.update(completed=True, views=count, covered_source_chunks=len(covered),
                    skipped_source_chunks=len(records) - len(covered), generation_seconds=time.perf_counter() - started,
                    views_sha256=hashlib.sha256(args.output.read_bytes()).hexdigest())
    manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()

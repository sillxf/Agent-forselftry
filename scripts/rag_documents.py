"""Inspect managed identities or explicitly map a renamed source; no LLM calls."""
import argparse
import json
from pathlib import Path
import sqlite3
import sys
from filelock import Timeout

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import RAG_KNOWLEDGE_DIR, RAG_STORAGE_DIR
from app.rag.lifecycle.service import LifecycleService


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage-dir", type=Path, default=RAG_STORAGE_DIR)
    parser.add_argument("--knowledge-dir", type=Path, default=RAG_KNOWLEDGE_DIR)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("list", help="List registered documents without loading a model")
    commands.add_parser("jobs", help="List persistent build jobs")
    gc = commands.add_parser("gc", help="Collect old generations and unreferenced artifacts; never purge source versions")
    gc.add_argument("--keep", type=int, default=3)
    gc.add_argument("--min-age-seconds", type=int, default=86400)
    for name in ("delete", "restore"):
        command = commands.add_parser(name, help=f"{name.title()} a logical document")
        command.add_argument("document_id")
    validity = commands.add_parser("validity", help="Replace both document validity bounds; omit a bound to clear it")
    validity.add_argument("document_id")
    validity.add_argument("--effective-at")
    validity.add_argument("--expires-at")
    rollback = commands.add_parser("rollback", help="Publish a managed historical generation; tombstones still apply")
    rollback.add_argument("generation")
    versions = commands.add_parser("versions", help="List immutable content versions")
    versions.add_argument("document_id")
    rename = commands.add_parser("rename", help="Map an already renamed file; content and type must be unchanged")
    rename.add_argument("document_id")
    rename.add_argument("source", type=Path)
    commands.add_parser("rebuild", help="Explicitly rebuild the configured knowledge directory; may load local models")
    args = parser.parse_args()
    service = LifecycleService(args.storage_dir)
    try:
        if args.command == "list":
            output = [item.model_dump() for item in service.registry.list_documents()]
        elif args.command == "versions":
            output = [item.model_dump() for item in service.registry.list_versions(args.document_id)]
        elif args.command == "jobs":
            output = service.registry.list_jobs()
        elif args.command in {"delete", "restore"}:
            output = getattr(service, args.command)(args.document_id).model_dump()
        elif args.command == "validity":
            output = service.set_validity(args.document_id, effective_at=args.effective_at, expires_at=args.expires_at).model_dump()
        elif args.command == "rename":
            output = service.rename(args.document_id, args.source).model_dump()
        else:
            from app.rag.retriever import KnowledgeRetriever
            retriever = KnowledgeRetriever(build=False, knowledge_dir=args.knowledge_dir, storage_dir=args.storage_dir)
            if args.command == "gc":
                from app.rag.indexing.maintenance import collect_generations
                output = collect_generations(retriever.build_service, keep=args.keep, min_age_seconds=args.min_age_seconds)
                print(json.dumps(output, ensure_ascii=False, indent=2))
                return
            if args.command == "rollback":
                retriever.rollback_generation(args.generation)
            else:
                retriever.build_index()
            output = json.loads((retriever.repository.root / "current.json").read_text(encoding="utf-8"))
    except (KeyError, ValueError, RuntimeError, Timeout, sqlite3.IntegrityError) as exc:
        parser.error(str(exc))
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

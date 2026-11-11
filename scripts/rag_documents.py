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
    rebuild = commands.add_parser("rebuild", help="Explicitly build and publish; incrementally reuse unchanged documents")
    rebuild.add_argument("--full", action="store_true", help="Force all derived indexes to be rebuilt")
    restore_version = commands.add_parser("restore-version", help="Select historical content, then rebuild to publish")
    restore_version.add_argument("document_id")
    restore_version.add_argument("version_id")
    purge = commands.add_parser("purge", help="Irreversibly purge managed content/history; external backups excluded")
    purge.add_argument("document_id")
    purge.add_argument("--confirm", action="store_true", required=True)
    configure = commands.add_parser("configure", help="Set document metadata or opt-in ViewConfig JSON")
    configure.add_argument("document_id")
    configure.add_argument("--metadata-json")
    configure.add_argument("--views-json")
    source = commands.add_parser("import", help="Capture a local source; sources outside knowledge-dir are added to the build inputs")
    source.add_argument("source", type=Path)
    policy = commands.add_parser("policy", help="Read or replace administrator retrieval policy")
    policy.add_argument("--json")
    commands.add_parser("generations", help="List committed publication history")
    search = commands.add_parser("search", help="Retrieve original evidence, optionally at a historical publication time")
    search.add_argument("query")
    search.add_argument("--as-of")
    search.add_argument("--supplement", action="store_true")
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
        elif args.command == "configure":
            from app.rag.view_generation import ViewConfig
            output = service.registry.configure(args.document_id,
                metadata=json.loads(args.metadata_json) if args.metadata_json else None,
                view_config=ViewConfig.model_validate_json(args.views_json).model_dump() if args.views_json else None).model_dump()
        elif args.command == "import":
            document, version = service.import_document(args.source)
            output = {"document":document.model_dump(), "version":version.model_dump(), "needs_build":True}
        elif args.command == "rename":
            output = service.rename(args.document_id, args.source).model_dump()
        else:
            from app.rag.retriever import KnowledgeRetriever
            retriever = KnowledgeRetriever(build=False, knowledge_dir=args.knowledge_dir, storage_dir=args.storage_dir)
            if args.command == "restore-version":
                output = retriever.restore_version(args.document_id, args.version_id).model_dump()
            elif args.command == "purge":
                output = retriever.purge_document(args.document_id)
            elif args.command == "generations":
                output = retriever.repository.publications()
            elif args.command == "search":
                output = retriever.search_with_trace(args.query, as_of=args.as_of, supplement=args.supplement)
            elif args.command == "policy":
                output = (retriever.set_policy(json.loads(args.json)) if args.json else retriever.orchestrator.policy).model_dump()
            elif args.command == "gc":
                from app.rag.indexing.maintenance import collect_generations
                output = collect_generations(retriever.build_service, keep=args.keep, min_age_seconds=args.min_age_seconds)
                print(json.dumps(output, ensure_ascii=False, indent=2))
                return
            elif args.command in {"rollback", "rebuild"}:
                if args.command == "rollback":
                    retriever.rollback_generation(args.generation)
                else:
                    retriever.build_index(full=args.full)
                output = json.loads((retriever.repository.root / "current.json").read_text(encoding="utf-8"))
    except (KeyError, ValueError, RuntimeError, Timeout, sqlite3.IntegrityError) as exc:
        parser.error(str(exc))
    print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

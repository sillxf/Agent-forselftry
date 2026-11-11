"""Explicit local storage migration: offline backup first, then build/publish. No benchmark."""
import argparse
import hashlib
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from app.config import RAG_KNOWLEDGE_DIR, RAG_STORAGE_DIR
from app.rag.retriever import KnowledgeRetriever


def backup_storage(storage, knowledge, destination, *, legacy_code_ref):
    storage, knowledge, destination = Path(storage).resolve(), Path(knowledge).resolve(), Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(storage) or destination.is_relative_to(knowledge):
        raise ValueError("Use a new backup directory outside storage and source directories")
    destination.mkdir(parents=True)
    shutil.copytree(storage, destination / "storage")
    shutil.copytree(knowledge, destination / "knowledge")
    registry = storage / "registry.db"
    if registry.exists():
        with sqlite3.connect(registry) as source, sqlite3.connect(destination / "storage/registry.db") as target:
            source.backup(target)
    # Preserve the exact chosen legacy code, not just a label pointing to dirty current sources.
    revision = subprocess.check_output(["git", "rev-parse", legacy_code_ref], text=True).strip()
    subprocess.run(["git", "archive", "--format=zip", "-o", str(destination / "legacy-code.zip"), revision], check=True)
    metadata = {"legacy_code_revision":revision, "storage_path":str(storage), "knowledge_path":str(knowledge),
        "files":{str(p.relative_to(destination)):hashlib.sha256(p.read_bytes()).hexdigest()
                 for p in destination.rglob("*") if p.is_file()}}
    (destination / "backup.json").write_text(json.dumps(metadata, indent=2), encoding="utf-8")
    return metadata


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--storage-dir", type=Path, default=RAG_STORAGE_DIR)
    parser.add_argument("--knowledge-dir", type=Path, default=RAG_KNOWLEDGE_DIR)
    parser.add_argument("--backup-dir", type=Path, required=True)
    parser.add_argument("--legacy-code-ref", required=True, help="Code compatible with the current storage; saved in backup")
    parser.add_argument("--apply", action="store_true", help="Required: confirms service/writers are stopped")
    args = parser.parse_args()
    if not args.apply:
        parser.error("Stop service and writers, then explicitly pass --apply")
    retriever = KnowledgeRetriever(build=False, storage_dir=args.storage_dir, knowledge_dir=args.knowledge_dir)
    retriever.storage_dir.mkdir(parents=True, exist_ok=True)
    with retriever.build_service.lock, retriever.lifecycle.source_lock:
        backup_storage(args.storage_dir, args.knowledge_dir, args.backup_dir, legacy_code_ref=args.legacy_code_ref)
        job = retriever.build_index(full=True)
        output = {"backup":str(args.backup_dir.resolve()), "job_id":job,
                  "current":retriever.repository.current_pointer(), "metrics":retriever.last_build_metrics}
        (args.backup_dir / "migration.json").write_text(json.dumps(output, indent=2), encoding="utf-8")
        print(json.dumps(output, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

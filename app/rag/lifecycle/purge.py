"""Resumable application-scope purge. External originals/backups are not erased."""
import json
import re
import shutil
import sqlite3
from contextlib import closing
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from filelock import FileLock

from app.rag.indexing.pipeline import IndexSnapshot
from app.rag.retrieval.sparse import SparseRetriever


def atomic_json(path, payload):
    path.parent.mkdir(parents=True, exist_ok=True)
    temp = path.with_name("." + uuid4().hex + ".tmp")
    try:
        temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)


def remove_managed(path, root):
    """One Python filesystem API, resolved containment checked before every removal."""
    path, root = Path(path), Path(root).resolve()
    if path.is_symlink() or not path.resolve().is_relative_to(root) or path.resolve() == root:
        raise ValueError("Refusing purge outside the managed asset root")
    if path.is_dir():
        shutil.rmtree(path)
    else:
        path.unlink(missing_ok=True)


def purge_document(owner, document_id):
    if not re.fullmatch(r"[0-9a-fA-F-]{36}", document_id):
        raise ValueError("Invalid document identifier")
    root = owner.storage_dir.resolve()
    plan_path = root / "purges" / (document_id + ".json")
    with owner.build_service.lock, owner.lifecycle.source_lock:
        document = owner.registry.get_document(document_id)
        if plan_path.exists():
            plan = json.loads(plan_path.read_text(encoding="utf-8"))
            if plan["status"] == "completed":
                return plan
        else:
            if document.purged_at:
                raise ValueError("Purge recovery plan is missing; restore storage before proceeding")
            versions = owner.registry.list_versions(document_id)
            generations = []
            for path in owner.repository.root.iterdir():
                if not path.is_dir() or not re.fullmatch(r"[0-9a-f]{32}", path.name):
                    continue
                try:
                    if not (path / "metadata.db").exists():
                        raise ValueError("Incomplete unpublished generation")
                    with closing(sqlite3.connect(path / "metadata.db")) as connection:
                        rows = [json.loads(row[0]) for row in connection.execute("SELECT data FROM documents")]
                    contains = any(r["document_id"] == document_id or r["source_path"] == document.source_path for r in rows)
                except (ValueError, sqlite3.DatabaseError):
                    # Incomplete disposable output may contain bytes but no usable identity map.
                    # Remove it too; a healthy published generation is still required below.
                    contains = True
                if contains:
                    generations.append(path.name)
            plan = {"document_id":document_id, "status":"planned", "generations":generations,
                "source_path":document.source_path, "source_hashes":sorted({v.content_hash for v in versions}),
                "created_at":datetime.now(timezone.utc).isoformat()}
            atomic_json(plan_path, plan)
        job = owner.registry.start_job("purge", owner.build_service._generation())
        try:
            if not document.purged_at:
                owner.registry.mark_purged(document_id)  # All old in-memory runtimes fail closed now.
            published = owner.repository.load_published()
            if not published or published[1]["signature"].get("version", 0) < 8:
                raise ValueError("Publish a managed format-8 generation before purging")
            snapshot, pointer = published
            if any(d.document_id == document_id for d in snapshot.documents):
                excluded = {r["chunk_id"] for r in snapshot.store.records if r["document_id"] == document_id}
                store = snapshot.store.updated(excluded, [], [])
                sparse = (snapshot.sparse or SparseRetriever(snapshot.store.records)).updated(store.records)
                view_store = snapshot.view_store
                if view_store:
                    ids = {r["chunk_id"] for r in view_store.records if r["source_child_id"] in excluded}
                    view_store = view_store.updated(ids, [], [])
                    if not view_store.records:
                        view_store = None
                retained_keys = []
                original_records = list(snapshot.store.records) + (list(snapshot.view_store.records) if snapshot.view_store else [])
                remaining_ids = {r["chunk_id"] for r in store.records} | ({r["chunk_id"] for r in view_store.records} if view_store else set())
                if len(original_records) == len(snapshot.embedding_cache_keys):
                    retained_keys = [key for r, key in zip(original_records, snapshot.embedding_cache_keys, strict=True) if r["chunk_id"] in remaining_ids]
                cleaned = IndexSnapshot(store, [d for d in snapshot.documents if d.document_id != document_id],
                    [p for p in snapshot.parents if p.document_id != document_id], view_store,
                    snapshot.view_model_name if view_store else None, embedding_cache_keys=retained_keys, sparse=sparse)
                signature, _ = owner._signature()
                owner._publish_snapshot(cleaned, signature, job_id=job, expected_generation=pointer["generation"])
            # A retry may already be serving the clean generation.
            revoked_path = owner.repository.root / "revoked.json"
            revoked = set(json.loads(revoked_path.read_text()) if revoked_path.exists() else [])
            revoked.update(plan["generations"])
            atomic_json(revoked_path, sorted(revoked))
            previous = owner.repository.root / "previous.json"
            if previous.exists() and json.loads(previous.read_text())["generation"] in revoked:
                previous.unlink()  # Never recover to a snapshot containing purged material.
            for identity in plan["generations"]:
                if identity == owner.repository.current_pointer()["generation"]:
                    raise ValueError("Cannot remove the current generation")
                with FileLock(str(owner.repository.root / (".read-" + identity + ".lock")), timeout=10):
                    remove_managed(owner.repository.root / identity, owner.repository.root)
            others = [v for d in owner.registry.list_documents() if d.document_id != document_id
                      for v in owner.registry.list_versions(d.document_id)]
            shared_hashes = {v.content_hash for v in others}
            for digest in plan["source_hashes"]:
                if digest in shared_hashes:
                    continue
                if not re.fullmatch(r"[0-9a-f]{64}", digest):
                    raise ValueError("Invalid source hash in purge plan")
                remove_managed(root / "sources" / digest, root / "sources")
                remove_managed(root / "images" / digest, root / "images")
                for extension in ("json", "md"):
                    remove_managed(root / "parsed" / (digest + "." + extension), root / "parsed")
            for directory in ("artifacts", "views"):
                for path in (root / directory).glob("*.json"):
                    try:
                        wrapper = json.loads(path.read_text(encoding="utf-8"))
                    except (ValueError, UnicodeError):
                        remove_managed(path, root / directory)  # Corrupt disposable caches cannot retain unknown content.
                        continue
                    payload = wrapper.get("payload", wrapper)
                    ids = {payload.get("document_id")}
                    ids.update(d.get("document_id") for d in payload.get("parents", []))
                    if document_id in ids:
                        remove_managed(path, root / directory)
            # Remove unreferenced vectors, retaining caches needed by other snapshots.
            referenced, referenced_artifacts = set(), set()
            for manifest in owner.repository.root.glob("*/manifest.json"):
                if re.fullmatch(r"[0-9a-f]{32}", manifest.parent.name):
                    retained_manifest = json.loads(manifest.read_text(encoding="utf-8"))
                    referenced.update(retained_manifest.get("embedding_cache_keys", []))
                    referenced_artifacts.update(d["artifact_id"] for d in retained_manifest["documents"] if d.get("artifact_id"))
            for path in (root / "artifacts").glob("*.json"):
                if path.stem not in referenced_artifacts:
                    remove_managed(path, root / "artifacts")
            # Interrupted builds/imports may leave disposable temporary files with source text.
            for directory in ("artifacts", "views", "embedding_cache"):
                for path in (root / directory).glob("*.tmp"):
                    remove_managed(path, root / directory)
            for path in (root / "sources").glob("tmp*"):
                if path.is_file():
                    remove_managed(path, root / "sources")
            for path in (root / "embedding_cache").glob("*.npz"):
                if path.stem not in referenced:
                    remove_managed(path, root / "embedding_cache")
            source = Path(plan["source_path"])
            external_preserved = not source.resolve().is_relative_to(owner.knowledge_dir.resolve())
            if not external_preserved:
                remove_managed(source, owner.knowledge_dir)
            owner.registry.finish_purge(document_id)
            with closing(sqlite3.connect(owner.registry.path)) as connection:
                connection.execute("VACUUM")
            result = {"document_id":document_id, "status":"completed", "external_original_preserved":external_preserved,
                "backup_erasure":"not_in_scope", "completed_at":datetime.now(timezone.utc).isoformat()}
            atomic_json(plan_path, result)
            owner.registry.finish_job(job, metrics={"purged_generations":len(plan["generations"])})
            return result
        except Exception as exc:
            plan["status"] = "failed"
            plan["error"] = type(exc).__name__
            atomic_json(plan_path, plan)
            owner.registry.finish_job(job, error=exc)
            raise

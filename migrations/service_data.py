"""Offline, explicit backup/restore/migration. Never overwrite existing destinations."""

from contextlib import ExitStack, closing
from pathlib import Path
import hashlib, json, os, shutil, sqlite3, subprocess
from uuid import uuid4
from filelock import FileLock
from app.storage.database import Database
from app.knowledge.catalog import KnowledgeBaseRepository
from app.ingestion.docling_parser import file_checksum
from app.storage.snapshot_repository import SnapshotRepository

PATH_KEYS = {
    "source_path",
    "source_blob_path",
    "image_path",
    "image_paths",
    "path",
    "path_key",
    "source_key",
}


def copy_tree(source, destination):
    source = Path(source).resolve()
    destination = Path(destination).resolve()
    if destination.exists():
        raise ValueError("Backup/migration destination must not already exist")
    if destination.is_relative_to(source) or source.is_relative_to(destination):
        raise ValueError("Source and destination must not overlap")
    # Avoid following links into unrelated data or silently omitting mounted source content.
    if any(p.is_symlink() for p in source.rglob("*")):
        raise ValueError(
            "Symlinked storage requires explicit export; refusing ambiguous backup"
        )
    shutil.copytree(
        source, destination, ignore=shutil.ignore_patterns("*-wal", "*-shm", "*.lock")
    )
    for p in source.rglob("*"):
        if p.is_file() and p.suffix in {".db", ".sqlite3"}:
            target = destination / p.relative_to(source)
            with (
                closing(sqlite3.connect(p)) as old,
                closing(sqlite3.connect(target)) as new,
            ):
                old.backup(new)


def inventory(root):
    return {
        p.relative_to(root).as_posix(): file_checksum(p)
        for p in sorted(Path(root).rglob("*"))
        if p.is_file()
    }


def verify_backup(backup):
    backup = Path(backup).resolve()
    manifest = json.loads((backup / "manifest.json").read_text(encoding="utf-8"))
    if manifest["files"] != inventory(backup / "snapshot"):
        raise ValueError("Backup file inventory/checksum mismatch")
    return manifest


def offline(root):
    stack = ExitStack()
    root = Path(root)
    try:
        for name in ["server.lock", "worker.lock"]:
            stack.enter_context(FileLock(str(root / name), timeout=0))
        return stack
    except BaseException:
        stack.close()
        raise


def backup_service(root, destination):
    root = Path(root).resolve()
    destination = Path(destination).resolve()
    if destination.exists() or destination.is_relative_to(root):
        raise ValueError("Use a new backup directory outside the live data root")
    with offline(root):
        destination.mkdir(mode=0o700, parents=True)
        copy_tree(root, destination / "snapshot")
        manifest = {
            "schema_version": 1,
            "kind": "rag-service",
            "original_root": str(root),
            "files": inventory(destination / "snapshot"),
        }
        (destination / "manifest.json").write_text(
            json.dumps(manifest, indent=2), encoding="utf-8"
        )
        verify_backup(destination)
    return manifest


def relocate_storage(storage, mappings):
    """Rebase metadata paths, not document text or immutable raw source bytes."""
    storage = Path(storage)

    def normal(value):
        return str(value).replace("\\", "/").rstrip("/")

    mappings = sorted(
        [(normal(a), str(Path(b).resolve())) for a, b in mappings],
        key=lambda x: -len(x[0]),
    )

    def rebase(value):
        if not isinstance(value, str):
            return value
        prefix = "path:" if value.startswith("path:") else ""
        raw = normal(value[len(prefix) :])
        for old, new in mappings:
            windows = (len(old) > 1 and old[1] == ":") or old.startswith("//")
            a, b = (raw.casefold(), old.casefold()) if windows else (raw, old)
            if a == b or a.startswith(b + "/"):
                suffix = raw[len(old) :].lstrip("/")
                result = str(Path(new).joinpath(*suffix.split("/"))) if suffix else new
                return prefix + (
                    os.path.normcase(result)
                    if prefix or value == os.path.normcase(value)
                    else result
                )
        return value

    def walk(value, key=None):
        if isinstance(value, dict):
            return {
                k: (
                    v
                    if k in {"table_data", "metadata", "structured_data"}
                    else walk(v, k)
                )
                for k, v in value.items()
            }
        if isinstance(value, list):
            return [walk(v, key) for v in value]
        return rebase(value) if key in PATH_KEYS else value

    for p in storage.rglob("*"):
        if not p.is_file() or "sources" in p.relative_to(storage).parts:
            continue
        if p.suffix == ".json":
            value = walk(json.loads(p.read_text(encoding="utf-8")))
            if isinstance(value, dict) and "payload" in value and "sha256" in value:
                value["sha256"] = hashlib.sha256(
                    json.dumps(
                        value["payload"],
                        sort_keys=True,
                        ensure_ascii=False,
                        separators=(",", ":"),
                    ).encode()
                ).hexdigest()
            p.write_text(
                json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
            )
        elif p.suffix == ".jsonl":
            p.write_text(
                "".join(
                    json.dumps(walk(json.loads(line)), ensure_ascii=False) + "\n"
                    for line in p.read_text(encoding="utf-8").splitlines()
                    if line.strip()
                ),
                encoding="utf-8",
            )
        elif p.suffix == ".db":
            with closing(sqlite3.connect(p)) as c, c:
                tables = [
                    r[0]
                    for r in c.execute(
                        "SELECT name FROM sqlite_master WHERE type='table'"
                    )
                ]
                for table in tables:
                    columns = [r[1] for r in c.execute(f'PRAGMA table_info("{table}")')]
                    for column in columns:
                        if column not in PATH_KEYS | {"data"}:
                            continue
                        for rowid, value in c.execute(
                            f'SELECT rowid,"{column}" FROM "{table}"'
                        ).fetchall():
                            updated = (
                                json.dumps(walk(json.loads(value)), ensure_ascii=False)
                                if column == "data"
                                else rebase(value)
                            )
                            c.execute(
                                f'UPDATE "{table}" SET "{column}"=? WHERE rowid=?',
                                (updated, rowid),
                            )
    # Recompute checksums only after all referenced metadata has been rewritten.
    for p in (storage / "indexes").glob("*/manifest.json"):
        value = json.loads(p.read_text(encoding="utf-8"))
        if "files" in value:
            value["files"] = {
                name: file_checksum(p.parent / name) for name in value["files"]
            }
            p.write_text(
                json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8"
            )
    repository = SnapshotRepository(storage)
    pointer = repository.current_pointer()
    if pointer:
        repository.load_generation(
            pointer["generation"], expected_signature=pointer["signature"]
        )


def restore_service(backup, destination):
    backup = Path(backup).resolve()
    destination = Path(destination).resolve()
    manifest = verify_backup(backup)
    if manifest["kind"] != "rag-service":
        raise ValueError("Not a complete service backup")
    if destination.exists():
        raise ValueError(
            "Restore only to a new directory; never overwrite a live service"
        )
    copy_tree(backup / "snapshot", destination)
    old = manifest["original_root"]
    for base in (destination / "bases").iterdir():
        if base.is_dir() and (base / "storage").exists():
            relocate_storage(base / "storage", [(old, destination)])
    database = Database(destination)
    catalog = KnowledgeBaseRepository(database)
    from app.indexing.repository import JobRepository

    JobRepository(database.connect, catalog.kb).recover()
    return {"root": str(destination), "knowledge_bases": len(catalog.list_kbs())}


def migrate_legacy(service, knowledge, storage, backup, *, writers_stopped=False):
    if not writers_stopped:
        raise ValueError(
            "Stop the legacy service/writers and explicitly confirm writers_stopped"
        )
    knowledge, storage, backup = map(
        lambda p: Path(p).resolve(), (knowledge, storage, backup)
    )
    if (
        backup.exists()
        or backup.is_relative_to(storage)
        or backup.is_relative_to(knowledge)
    ):
        raise ValueError("Use a new external backup directory")
    if not storage.is_dir() or not knowledge.is_dir():
        raise ValueError("Legacy storage and knowledge directories are required")
    if any(
        service.workspaces.get(k["id"]).repository.current_pointer()
        for k in service.knowledge.repository.list_kbs()
    ):
        raise ValueError(
            "Import into a fresh service data root, not an already published service"
        )
    with (
        offline(service.root),
        FileLock(str(storage / "build.lock"), timeout=0),
        FileLock(str(storage / "sources.lock"), timeout=0),
    ):
        backup.mkdir(parents=True, mode=0o700)
        snapshot = backup / "snapshot"
        snapshot.mkdir()
        copy_tree(storage, snapshot / "storage")
        copy_tree(knowledge, snapshot / "knowledge")
        (backup / "manifest.json").write_text(
            json.dumps(
                {
                    "schema_version": 1,
                    "kind": "legacy-rag",
                    "files": inventory(snapshot),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        verify_backup(backup)
        try:
            subprocess.run(
                [
                    "git",
                    "archive",
                    "--format=zip",
                    "-o",
                    str(backup / "legacy-code.zip"),
                    "HEAD",
                ],
                cwd=knowledge.parent.parent,
                check=True,
                capture_output=True,
            )
        except (OSError, subprocess.CalledProcessError):
            pass
        identity = uuid4().hex
        stage = service.root / ("migration-" + identity)
        final = service.root / "bases" / identity
        stage.mkdir()
        copy_tree(snapshot / "storage", stage / "storage")
        copy_tree(snapshot / "knowledge", stage / "knowledge")
        mappings = [(storage, final / "storage"), (knowledge, final / "knowledge")]
        registry = stage / "storage/registry.db"
        with closing(sqlite3.connect(registry)) as c, c:
            for doc_id, source, version in c.execute(
                "SELECT document_id,source_path,latest_version_id FROM documents WHERE purged_at IS NULL"
            ).fetchall():
                if not Path(source).resolve().is_relative_to(knowledge):
                    row = c.execute(
                        "SELECT source_blob_path FROM document_versions WHERE version_id=?",
                        (version,),
                    ).fetchone()
                    target = stage / "knowledge" / (doc_id + "_" + Path(source).name)
                    shutil.copy2(row[0], target)
                    mappings.append((Path(source), final / "knowledge" / target.name))
        relocate_storage(stage / "storage", mappings)
        # Verify staged bytes. Paths point to the final root; raw blobs are byte-identical copies.
        if not stage.resolve().is_relative_to(
            service.root
        ) or not final.resolve().is_relative_to(service.root):
            raise ValueError("Migration paths escaped the service root")
        stage.rename(final)
        config = dict(
            name="Migrated knowledge",
            description="Imported knowledge; immutable IDs/history retained",
        )
        service.knowledge.repository.create_kb(config, identity=identity)
        result = {
            "knowledge_base_id": identity,
            "backup": str(backup),
            "legacy_writes": "must remain stopped; use the independent RAG API",
            "current": service.workspaces.get(identity).repository.current_pointer(),
        }
        (service.root / "migration.json").write_text(
            json.dumps(result, indent=2), encoding="utf-8"
        )
        service.audit.audit("migration", "legacy_imported", identity)
        (storage / "service-cutover.json").write_text(
            json.dumps(
                {
                    "knowledge_base_id": identity,
                    "service_data": str(service.root),
                    "status": "retired_writer",
                    "backup": str(backup),
                },
                indent=2,
            ),
            encoding="utf-8",
        )
        return result

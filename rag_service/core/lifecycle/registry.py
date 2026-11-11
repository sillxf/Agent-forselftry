"""Small transactional registry. Constructing it never creates files or loads models."""

import os
import json
import sqlite3
from contextlib import closing, contextmanager
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4

from rag_service.core.models import DocumentVersion, KnowledgeDocument


_SCHEMA = """
CREATE TABLE IF NOT EXISTS registry_meta (
    singleton INTEGER PRIMARY KEY CHECK (singleton = 1),
    schema_version INTEGER NOT NULL,
    lifecycle_revision INTEGER NOT NULL
);
INSERT OR IGNORE INTO registry_meta VALUES (1, 1, 0);
CREATE TABLE IF NOT EXISTS documents (
    document_id TEXT PRIMARY KEY,
    source_key TEXT NOT NULL UNIQUE,
    source_path TEXT NOT NULL,
    path_key TEXT NOT NULL UNIQUE,
    latest_version_id TEXT REFERENCES document_versions(version_id),
    created_at TEXT NOT NULL,
    updated_at TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS document_versions (
    version_id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(document_id),
    version_number INTEGER NOT NULL CHECK (version_number > 0),
    content_hash TEXT NOT NULL,
    source_blob_path TEXT NOT NULL,
    file_type TEXT NOT NULL,
    created_at TEXT NOT NULL,
    UNIQUE (document_id, version_number),
    UNIQUE (document_id, content_hash, file_type)
);
"""


def path_key(path):
    return os.path.normcase(str(Path(path).resolve()))


class DocumentRegistry:
    def __init__(self, storage_dir):
        self.path = Path(storage_dir) / "registry.db"
        self._initialized = False

    @contextmanager
    def _connection(self):
        if (self.path.parent / "service-cutover.json").exists():
            raise ValueError(
                "Legacy storage was migrated; use the independent service or restore the pre-migration backup"
            )
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with closing(sqlite3.connect(self.path, timeout=10)) as connection:
            connection.row_factory = sqlite3.Row
            connection.execute("PRAGMA foreign_keys = ON")
            connection.execute("PRAGMA secure_delete = ON")
            if not self._initialized:
                connection.executescript(_SCHEMA)
                connection.execute("BEGIN IMMEDIATE")
                schema = connection.execute(
                    "SELECT schema_version FROM registry_meta"
                ).fetchone()[0]
                if schema == 1:
                    for column in ("deleted_at", "effective_at", "expires_at"):
                        connection.execute(
                            f"ALTER TABLE documents ADD COLUMN {column} TEXT"
                        )
                    connection.execute("""CREATE TABLE build_jobs (
                        job_id TEXT PRIMARY KEY, kind TEXT NOT NULL, status TEXT NOT NULL,
                        input_revision INTEGER NOT NULL, expected_generation_id TEXT,
                        output_generation_id TEXT, error_code TEXT, error_message TEXT,
                        created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                    )""")
                    connection.execute("UPDATE registry_meta SET schema_version = 2")
                    schema = 2
                if schema == 2:
                    connection.execute(
                        "ALTER TABLE build_jobs ADD COLUMN metrics_json TEXT"
                    )
                    connection.execute("UPDATE registry_meta SET schema_version = 3")
                    schema = 3
                if schema == 3:
                    for column in (
                        "selected_version_id TEXT",
                        "purged_at TEXT",
                        "metadata_json TEXT NOT NULL DEFAULT '{}'",
                        "view_config_json TEXT NOT NULL DEFAULT '{}'",
                    ):
                        connection.execute(f"ALTER TABLE documents ADD COLUMN {column}")
                    connection.execute(
                        "CREATE TABLE purged_sources (path_hash TEXT PRIMARY KEY, document_id TEXT NOT NULL)"
                    )
                    connection.execute("""CREATE TABLE view_artifacts (
                        cache_key TEXT PRIMARY KEY, document_id TEXT NOT NULL, version_id TEXT NOT NULL,
                        artifact_id TEXT NOT NULL, config_json TEXT NOT NULL, status TEXT NOT NULL,
                        error TEXT, usage_json TEXT, updated_at TEXT NOT NULL)""")
                    connection.execute("UPDATE registry_meta SET schema_version = 4")
                    schema = 4
                if schema != 4:
                    raise ValueError("Unsupported document registry schema")
                connection.commit()
                self._initialized = True
            with connection:
                yield connection

    @staticmethod
    def _document(row):
        data = dict(row)
        data["metadata"] = json.loads(data.pop("metadata_json", "{}"))
        data["view_config"] = json.loads(data.pop("view_config_json", "{}"))
        return KnowledgeDocument.model_validate(data)

    @property
    def revision(self):
        if not self.path.exists():
            return 0
        with self._connection() as connection:
            return connection.execute(
                "SELECT lifecycle_revision FROM registry_meta"
            ).fetchone()[0]

    @staticmethod
    def _advance(connection):
        connection.execute(
            "UPDATE registry_meta SET lifecycle_revision = lifecycle_revision + 1"
        )

    def register_source(
        self, source_path, content_hash, source_blob_path, file_type, *, source_id=None
    ):
        """Idempotently register bytes. Equal bytes never merge different logical sources."""
        source_path = str(Path(source_path).resolve())
        key = path_key(source_path)
        if source_id is not None and not source_id.strip():
            raise ValueError("source_id must not be blank")
        external_key = f"external:{source_id}" if source_id is not None else None
        now = datetime.now(timezone.utc).isoformat()
        if self.is_blocked(source_path):
            raise ValueError("Source was purged; automatic reimport is blocked")
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            by_path = connection.execute(
                "SELECT * FROM documents WHERE path_key = ?", (key,)
            ).fetchone()
            row = (
                connection.execute(
                    "SELECT * FROM documents WHERE source_key = ?", (external_key,)
                ).fetchone()
                if external_key
                else by_path
            )
            if (
                external_key
                and by_path is not None
                and (row is None or row["document_id"] != by_path["document_id"])
            ):
                raise ValueError("Source path already belongs to a different document")
            changed = row is None
            if row is None:
                document_id = str(uuid4())
                connection.execute(
                    "INSERT INTO documents (document_id, source_key, source_path, path_key, latest_version_id, created_at, updated_at) VALUES (?, ?, ?, ?, NULL, ?, ?)",
                    (
                        document_id,
                        external_key or f"path:{key}",
                        source_path,
                        key,
                        now,
                        now,
                    ),
                )
                previous_version = None
            else:
                if row["deleted_at"] is not None:
                    raise ValueError(
                        "Document is deleted; restore it explicitly before importing"
                    )
                document_id = row["document_id"]
                previous_version = row["latest_version_id"]
                if row["source_path"] != source_path:
                    connection.execute(
                        "UPDATE documents SET source_path = ?, path_key = ? WHERE document_id = ?",
                        (source_path, key, document_id),
                    )
                    changed = True
            version = connection.execute(
                "SELECT * FROM document_versions WHERE document_id = ? AND content_hash = ? AND file_type = ?",
                (document_id, content_hash, file_type),
            ).fetchone()
            if version is None:
                version_id = str(uuid4())
                number = connection.execute(
                    "SELECT COALESCE(MAX(version_number), 0) + 1 FROM document_versions WHERE document_id = ?",
                    (document_id,),
                ).fetchone()[0]
                connection.execute(
                    "INSERT INTO document_versions VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (
                        version_id,
                        document_id,
                        number,
                        content_hash,
                        str(source_blob_path),
                        file_type,
                        now,
                    ),
                )
                version = connection.execute(
                    "SELECT * FROM document_versions WHERE version_id = ?",
                    (version_id,),
                ).fetchone()
            if previous_version != version["version_id"]:
                changed = True
            if changed:
                connection.execute(
                    "UPDATE documents SET latest_version_id = ?, updated_at = ? WHERE document_id = ?",
                    (version["version_id"], now, document_id),
                )
                if previous_version != version["version_id"]:
                    connection.execute(
                        "UPDATE documents SET selected_version_id = NULL WHERE document_id = ?",
                        (document_id,),
                    )
                    connection.execute(
                        "UPDATE view_artifacts SET status = 'stale' WHERE document_id = ?",
                        (document_id,),
                    )
                self._advance(connection)
            document = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
            return self._document(document), DocumentVersion.model_validate(
                dict(version)
            )

    def get_document(self, document_id):
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
            if row is None:
                raise KeyError(document_id)
            return self._document(row)

    def list_documents(self):
        if not self.path.exists():
            return []
        with self._connection() as connection:
            return [
                self._document(row)
                for row in connection.execute(
                    "SELECT * FROM documents ORDER BY source_path, document_id"
                )
            ]

    def list_versions(self, document_id):
        if not self.path.exists():
            return []
        with self._connection() as connection:
            return [
                DocumentVersion.model_validate(dict(row))
                for row in connection.execute(
                    "SELECT * FROM document_versions WHERE document_id = ? ORDER BY version_number",
                    (document_id,),
                )
            ]

    def rename(self, document_id, new_path):
        """Update a mapping after an explicit source rename, never infer identity from hashes."""
        new_path = str(Path(new_path).resolve())
        key = path_key(new_path)
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
            if row is None:
                raise KeyError(document_id)
            if row["purged_at"]:
                raise ValueError("Purged documents cannot be renamed")
            if row["source_path"] != new_path:
                source_key = (
                    f"path:{key}"
                    if row["source_key"].startswith("path:")
                    else row["source_key"]
                )
                connection.execute(
                    "UPDATE documents SET source_path = ?, path_key = ?, source_key = ?, updated_at = ? WHERE document_id = ?",
                    (
                        new_path,
                        key,
                        source_key,
                        datetime.now(timezone.utc).isoformat(),
                        document_id,
                    ),
                )
                self._advance(connection)
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
            return self._document(row)

    def lookup_path(self, source_path):
        if not self.path.exists():
            return None
        with self._connection() as connection:
            row = connection.execute(
                "SELECT * FROM documents WHERE path_key = ?", (path_key(source_path),)
            ).fetchone()
            return self._document(row) if row is not None else None

    def capture_sources(self, paths):
        """One read transaction fixes all selected versions and their lifecycle revision."""
        keys = {path_key(path) for path in paths}
        with self._connection() as connection:
            connection.execute("BEGIN")
            revision = connection.execute(
                "SELECT lifecycle_revision FROM registry_meta"
            ).fetchone()[0]
            selected = {}
            for row in connection.execute("SELECT * FROM documents"):
                if row["path_key"] in keys and row["deleted_at"] is None:
                    document = self._document(row)
                    version = connection.execute(
                        "SELECT * FROM document_versions WHERE version_id = ?",
                        (document.selected_version_id or document.latest_version_id,),
                    ).fetchone()
                    if version is None:
                        raise ValueError(
                            "Registered document is missing its content version"
                        )
                    selected[row["path_key"]] = (
                        document,
                        DocumentVersion.model_validate(dict(version)),
                    )
            return [
                selected[path_key(path)] for path in paths if path_key(path) in selected
            ], revision

    def eligible_ids(self, document_ids, *, at=None):
        """Authoritative live filter. Missing/corrupt registry must never bypass tombstones."""
        requested = set(document_ids)
        if not requested:
            return set()
        if not self.path.exists():
            raise ValueError(
                "Managed document registry is missing; restore the complete storage backup"
            )
        now = at or datetime.now(timezone.utc)
        with self._connection() as connection:
            rows = {
                row["document_id"]: row
                for row in connection.execute(
                    "SELECT document_id, deleted_at, purged_at, effective_at, expires_at FROM documents"
                )
            }
        if requested - rows.keys():
            raise ValueError(
                "Managed snapshot references documents absent from the registry"
            )
        return {
            key
            for key in requested
            if rows[key]["deleted_at"] is None
            and rows[key]["purged_at"] is None
            and (
                rows[key]["effective_at"] is None
                or datetime.fromisoformat(rows[key]["effective_at"]) <= now
            )
            and (
                rows[key]["expires_at"] is None
                or now < datetime.fromisoformat(rows[key]["expires_at"])
            )
        }

    def _update_lifecycle(self, document_id, fields):
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
            if row is None:
                raise KeyError(document_id)
            if row["purged_at"] is not None:
                raise ValueError("Purged documents cannot be modified")
            if any(row[key] != value for key, value in fields.items()):
                assignments = ", ".join(f"{key} = ?" for key in fields)
                connection.execute(
                    f"UPDATE documents SET {assignments}, updated_at = ? WHERE document_id = ?",
                    [
                        *fields.values(),
                        datetime.now(timezone.utc).isoformat(),
                        document_id,
                    ],
                )
                self._advance(connection)
            row = connection.execute(
                "SELECT * FROM documents WHERE document_id = ?", (document_id,)
            ).fetchone()
            return self._document(row)

    def set_deleted(self, document_id, deleted=True):
        document = self.get_document(document_id)
        if document.purged_at:
            raise ValueError("Purged documents cannot be restored or modified")
        timestamp = (
            (document.deleted_at or datetime.now(timezone.utc).isoformat())
            if deleted
            else None
        )
        return self._update_lifecycle(document_id, {"deleted_at": timestamp})

    def set_validity(self, document_id, *, effective_at=None, expires_at=None):
        def utc(value):
            if value is None:
                return None
            parsed = (
                datetime.fromisoformat(value.replace("Z", "+00:00"))
                if isinstance(value, str)
                else value
            )
            if parsed.tzinfo is None or parsed.utcoffset() is None:
                raise ValueError("Validity timestamps must include a timezone")
            return parsed.astimezone(timezone.utc).isoformat()

        effective_at, expires_at = utc(effective_at), utc(expires_at)
        if (
            effective_at
            and expires_at
            and datetime.fromisoformat(expires_at)
            <= datetime.fromisoformat(effective_at)
        ):
            raise ValueError("expires_at must be later than effective_at")
        return self._update_lifecycle(
            document_id, dict(effective_at=effective_at, expires_at=expires_at)
        )

    @contextmanager
    def publication_guard(self, expected_revision):
        """All lifecycle writers share SQLite's write lock with this short commit window."""
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            actual = connection.execute(
                "SELECT lifecycle_revision FROM registry_meta"
            ).fetchone()[0]
            if actual != expected_revision:
                raise RuntimeError(
                    f"Stale build: lifecycle revision changed ({expected_revision} -> {actual})"
                )
            yield

    def start_job(self, kind, expected_generation):
        now = datetime.now(timezone.utc).isoformat()
        job_id = str(uuid4())
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            revision = connection.execute(
                "SELECT lifecycle_revision FROM registry_meta"
            ).fetchone()[0]
            connection.execute(
                "INSERT INTO build_jobs (job_id, kind, status, input_revision, expected_generation_id, output_generation_id, error_code, error_message, created_at, updated_at) VALUES (?, ?, 'running', ?, ?, NULL, NULL, NULL, ?, ?)",
                (job_id, kind, revision, expected_generation, now, now),
            )
        return job_id

    def update_job_output(self, job_id, revision, generation):
        with self._connection() as connection:
            connection.execute(
                "UPDATE build_jobs SET input_revision = ?, output_generation_id = ?, updated_at = ? WHERE job_id = ?",
                (revision, generation, datetime.now(timezone.utc).isoformat(), job_id),
            )

    def finish_job(self, job_id, *, error=None, metrics=None):
        with self._connection() as connection:
            connection.execute(
                "UPDATE build_jobs SET status = ?, error_code = ?, error_message = ?, updated_at = ?, metrics_json = COALESCE(?, metrics_json) WHERE job_id = ?",
                (
                    "failed" if error else "succeeded",
                    type(error).__name__ if error else None,
                    str(error)[:2000] if error else None,
                    datetime.now(timezone.utc).isoformat(),
                    json.dumps(metrics) if metrics is not None else None,
                    job_id,
                ),
            )

    def list_jobs(self):
        if not self.path.exists():
            return []
        with self._connection() as connection:
            jobs = [
                dict(row)
                for row in connection.execute(
                    "SELECT * FROM build_jobs ORDER BY created_at DESC"
                )
            ]
            for job in jobs:
                job["metrics"] = json.loads(job.pop("metrics_json") or "{}")
            return jobs

    def recover_jobs(self, current_generation, previous_generation=None):
        """Caller must hold the build file lock: no other conforming worker can be running."""
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            for row in connection.execute(
                "SELECT * FROM build_jobs WHERE status = 'running'"
            ).fetchall():
                published = (
                    row["kind"] != "purge"
                    and row["output_generation_id"] is not None
                    and row["output_generation_id"]
                    in {current_generation, previous_generation}
                )
                connection.execute(
                    "UPDATE build_jobs SET status = ?, error_code = ?, error_message = ?, updated_at = ? WHERE job_id = ?",
                    (
                        "succeeded" if published else "failed",
                        None
                        if published
                        else "InterruptedMaintenance"
                        if row["kind"] == "purge"
                        else "InterruptedBuild",
                        None
                        if published
                        else "Worker stopped before purge completion; retry the purge plan"
                        if row["kind"] == "purge"
                        else "Worker stopped before publication; safe to retry",
                        datetime.now(timezone.utc).isoformat(),
                        row["job_id"],
                    ),
                )
            connection.execute(
                "UPDATE view_artifacts SET status='failed', error='Interrupted generation; safe to retry' WHERE status='running'"
            )

    def is_blocked(self, path):
        import hashlib

        if not self.path.exists():
            return False
        key = hashlib.sha256(path_key(path).encode()).hexdigest()
        with self._connection() as connection:
            return (
                connection.execute(
                    "SELECT 1 FROM purged_sources WHERE path_hash = ?", (key,)
                ).fetchone()
                is not None
            )

    def configure(self, document_id, *, metadata=None, view_config=None):
        document = self.get_document(document_id)
        if document.purged_at:
            raise ValueError("Purged documents cannot be modified")
        fields = {}
        if metadata is not None:
            fields["metadata_json"] = json.dumps(
                metadata, sort_keys=True, ensure_ascii=False
            )
        if view_config is not None:
            fields["view_config_json"] = json.dumps(
                view_config, sort_keys=True, ensure_ascii=False
            )
        result = self._update_lifecycle(document_id, fields) if fields else document
        if view_config is not None and document.view_config != view_config:
            with self._connection() as connection:
                connection.execute(
                    "UPDATE view_artifacts SET status = 'stale' WHERE document_id = ?",
                    (document_id,),
                )
        return result

    def select_version(self, document_id, version_id):
        document = self.get_document(document_id)
        if document.purged_at:
            raise ValueError("Purged document history is unavailable")
        if version_id not in {
            item.version_id for item in self.list_versions(document_id)
        }:
            raise KeyError(version_id)
        return self._update_lifecycle(
            document_id, {"selected_version_id": version_id, "deleted_at": None}
        )

    def set_view_state(self, key, document, config, status, *, error=None, usage=None):
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as connection:
            connection.execute(
                """INSERT INTO view_artifacts VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(cache_key) DO UPDATE SET status=excluded.status, error=excluded.error,
                usage_json=excluded.usage_json, updated_at=excluded.updated_at""",
                (
                    key,
                    document.document_id,
                    document.version_id,
                    document.artifact_id,
                    json.dumps(config, sort_keys=True),
                    status,
                    error,
                    json.dumps(usage or {}),
                    now,
                ),
            )

    def view_states(self, document_id=None):
        if not self.path.exists():
            return []
        with self._connection() as connection:
            rows = connection.execute(
                "SELECT * FROM view_artifacts"
                + (" WHERE document_id = ?" if document_id else "")
                + " ORDER BY updated_at DESC",
                (document_id,) if document_id else (),
            )
            return [dict(row) for row in rows]

    def purged_ids(self):
        if not self.path.exists():
            return set()
        with self._connection() as connection:
            return {
                row[0]
                for row in connection.execute(
                    "SELECT document_id FROM documents WHERE purged_at IS NOT NULL"
                )
            }

    def mark_purged(self, document_id):
        import hashlib

        document = self.get_document(document_id)
        key = hashlib.sha256(path_key(document.source_path).encode()).hexdigest()
        now = datetime.now(timezone.utc).isoformat()
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "INSERT OR IGNORE INTO purged_sources VALUES (?, ?)", (key, document_id)
            )
            connection.execute(
                "UPDATE documents SET purged_at = ?, deleted_at = ? WHERE document_id = ?",
                (now, now, document_id),
            )
            self._advance(connection)

    def finish_purge(self, document_id):
        with self._connection() as connection:
            connection.execute("BEGIN IMMEDIATE")
            connection.execute(
                "UPDATE documents SET latest_version_id=NULL, selected_version_id=NULL, "
                "metadata_json='{}', view_config_json='{}', source_path=?, path_key=?, source_key=? WHERE document_id=?",
                (
                    f"purged:{document_id}",
                    f"purged:{document_id}",
                    f"purged:{document_id}",
                    document_id,
                ),
            )
            connection.execute(
                "DELETE FROM document_versions WHERE document_id = ?", (document_id,)
            )
            connection.execute(
                "DELETE FROM view_artifacts WHERE document_id = ?", (document_id,)
            )
            self._advance(connection)

    def invalidate_views(self, document_id, *, except_key=None):
        with self._connection() as connection:
            connection.execute(
                "UPDATE view_artifacts SET status = 'stale' WHERE document_id = ? AND cache_key != ?",
                (document_id, except_key or ""),
            )

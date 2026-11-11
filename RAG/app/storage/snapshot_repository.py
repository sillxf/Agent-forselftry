"""Persist and publish local index generations without constructing query components."""

import json
import os
import sqlite3
from collections import OrderedDict
from contextlib import closing
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from threading import Lock
from uuid import uuid4
from filelock import FileLock

from app.core.exceptions import IndexIntegrityError, NotPublished

from app.indexing.pipeline import IndexSnapshot
from app.storage.vector_store import FaissVectorStore
from app.knowledge.models import DocumentRecord, ParentChunk
from app.ingestion.docling_parser import file_checksum
from app.indexing.view_models import RetrievalView, validate_views
from app.retrieval.strategies.sparse import SparseRetriever


@dataclass(frozen=True)
class SavedGeneration:
    generation: str
    signature: dict


class SnapshotRepository:
    """Generations on disk, plus small read caches for the query process.

    Verifying a generation hashes every asset, and loading one reads the whole
    index. Document and chunk reads did both on every call. Verified manifests
    and read-only snapshots are now reused while the files keep the same size
    and modification time; a revoked, removed or rewritten generation is never
    served from the cache. Builds and deletions still load private copies.
    """

    MANIFEST_CACHE = 32

    def __init__(self, storage_dir, store_factory=FaissVectorStore, *, cache_size=None):
        self.root = Path(storage_dir) / "indexes"
        self.store_factory = store_factory
        self.cache_size = (
            int(os.getenv("RAG_SNAPSHOT_CACHE_SIZE", "1"))
            if cache_size is None
            else cache_size
        )
        self._lock = Lock()
        self._manifests = OrderedDict()  # generation -> (stamp, manifest)
        self._snapshots = OrderedDict()  # generation -> (stamp, snapshot)
        self._publications = {}  # publication records never change once written

    def save(self, snapshot: IndexSnapshot, signature: dict) -> SavedGeneration:
        """Save a fresh generation; leave the current pointer and old files untouched."""
        self._validate_snapshot(snapshot)
        generation = uuid4().hex
        path = self.root / generation
        if (
            snapshot.view_store is not None
            and snapshot.view_model_name != signature["model"]
        ):
            raise ValueError(
                "View index and original index must use the same embedding model"
            )
        snapshot.store.save(path)
        if snapshot.view_store is not None:
            snapshot.view_store.save(path / "views")
            (path / "views/manifest.json").write_text(
                json.dumps(
                    {
                        "embedding_model": snapshot.view_model_name,
                        "view_type": "question",
                        "count": len(snapshot.view_store.records),
                    }
                ),
                encoding="utf-8",
            )
        with closing(sqlite3.connect(path / "metadata.db")) as connection, connection:
            connection.executescript("""
                CREATE TABLE documents (document_id TEXT PRIMARY KEY, data TEXT NOT NULL);
                CREATE TABLE parents (parent_id TEXT PRIMARY KEY, document_id TEXT, data TEXT NOT NULL);
                CREATE TABLE chunks (chunk_id TEXT PRIMARY KEY, parent_id TEXT, document_id TEXT);
            """)
            connection.executemany(
                "INSERT INTO documents VALUES (?, ?)",
                [
                    (doc.document_id, doc.model_dump_json())
                    for doc in snapshot.documents
                ],
            )
            connection.executemany(
                "INSERT INTO parents VALUES (?, ?, ?)",
                [
                    (p.parent_id, p.document_id, p.model_dump_json())
                    for p in snapshot.parents
                ],
            )
            connection.executemany(
                "INSERT INTO chunks VALUES (?, ?, ?)",
                [
                    (r["chunk_id"], r["parent_id"], r["document_id"])
                    for r in snapshot.store.records
                ],
            )
        sparse = snapshot.sparse or SparseRetriever(snapshot.store.records)
        (path / "sparse.json").write_text(
            json.dumps(sparse.payload(), ensure_ascii=False), encoding="utf-8"
        )
        files = ["faiss.index", "chunks.jsonl", "metadata.db", "sparse.json"]
        if snapshot.view_store is not None:
            files.extend(
                ["views/faiss.index", "views/chunks.jsonl", "views/manifest.json"]
            )
        manifest = {
            "schema_version": 1,
            "generation_id": generation,
            "created_at": datetime.now(timezone.utc).isoformat(),
            "signature": signature,
            "documents": self._document_refs(snapshot),
            "embedding_cache_keys": snapshot.embedding_cache_keys,
            "view_assets": self._view_refs(snapshot),
            "counts": {
                "documents": len(snapshot.documents),
                "parents": len(snapshot.parents),
                "children": len(snapshot.store.records),
            },
            "files": {name: file_checksum(path / name) for name in files},
        }
        (path / "manifest.json").write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8"
        )
        return SavedGeneration(generation, signature)

    def publish(self, saved: SavedGeneration, *, rollback=False) -> None:
        """Publish a validated snapshot under the caller's single-writer guard."""
        manifest = self._read_manifest(saved.generation)
        if manifest is None or manifest["signature"] != saved.signature:
            raise ValueError(
                "Generation manifest does not match the publication signature"
            )
        current = self.root / "current.json"
        if current.exists():
            # Keep a previously published pointer, never an unpublished ready directory.
            try:
                old = json.loads(current.read_text(encoding="utf-8"))
                self._read_manifest(old["generation"])
                previous = self.root / ".previous.tmp"
                previous.write_text(json.dumps(old), encoding="utf-8")
                previous.replace(self.root / "previous.json")
            except (OSError, ValueError, KeyError):
                pass  # Preserve the last known previous pointer if current is damaged.
        try:
            old = self.current_pointer()
        except (ValueError, OSError):
            old = None
        publication_id = uuid4().hex
        publication = {
            "publication_id": publication_id,
            "generation": saved.generation,
            "published_at": datetime.now(timezone.utc).isoformat(),
            "previous_publication_id": old.get("publication_id") if old else None,
            "rollback": rollback,
        }
        history = self.root / "publications"
        history.mkdir(exist_ok=True)
        (history / (publication_id + ".json")).write_text(
            json.dumps(publication), encoding="utf-8"
        )
        # Only records reachable from the atomically committed pointer count as published.
        payload = {**publication, "signature": saved.signature}
        if rollback:
            payload["rollback"] = True
        pointer = self.root / f".current-{saved.generation}.tmp"
        pointer.write_text(json.dumps(payload), encoding="utf-8")
        pointer.replace(self.root / "current.json")

    def _stamp(self, generation):
        """Name, size and mtime of every asset; None once the directory is gone."""
        path, items = self.root / generation, []
        for directory, label in ((path, ""), (path / "views", "views")):
            try:
                entries = list(os.scandir(directory))
            except FileNotFoundError:
                if not label:
                    return None
                continue
            for entry in entries:
                if entry.is_file():
                    stat = entry.stat()
                    items.append((label, entry.name, stat.st_mtime_ns, stat.st_size))
        return tuple(sorted(items))

    def load_generation(
        self, generation: str, *, expected_signature=None, cached=False
    ) -> IndexSnapshot:
        """cached=True returns a shared, read-only snapshot; never mutate it."""
        if (
            not isinstance(generation, str)
            or not generation
            or Path(generation).name != generation
            or generation in {".", ".."}
        ):
            raise ValueError("Invalid generation identifier")
        stamp = self._stamp(generation) if cached and self.cache_size > 0 else None
        if cached and stamp is None:
            with self._lock:  # Directory removed: release the stale copy.
                self._snapshots.pop(generation, None)
        if stamp is not None:
            with self._lock:
                hit = self._snapshots.get(generation)
                if hit is not None and hit[0] == stamp:
                    self._snapshots.move_to_end(generation)
                else:
                    hit = None
            if hit is not None:
                manifest = self._read_manifest(generation)  # Revocation and integrity.
                if expected_signature is not None and (
                    manifest["signature"] != expected_signature
                    if manifest is not None
                    else expected_signature.get("version", 0) >= 6
                ):
                    raise IndexIntegrityError(
                        "Current pointer differs from the generation manifest"
                    )
                return hit[1]
        # A short cold-load lease prevents retention from removing files mid-load.
        with FileLock(str(self.root / f".read-{generation}.lock"), timeout=10):
            snapshot = self._load_generation(
                generation, expected_signature=expected_signature
            )
        if stamp is not None:
            with self._lock:
                self._snapshots[generation] = (stamp, snapshot)
                self._snapshots.move_to_end(generation)
                while len(self._snapshots) > self.cache_size:
                    self._snapshots.popitem(last=False)
        return snapshot

    def _load_generation(self, generation, *, expected_signature=None):
        path = self.root / generation
        manifest = self._read_manifest(generation)
        if (
            manifest is not None
            and expected_signature is not None
            and manifest["signature"] != expected_signature
        ):
            raise IndexIntegrityError("Current pointer differs from the generation manifest")
        store = self.store_factory.load(path)
        for record in store.records:
            # Removed in 1.2 (never used by retrieval); older generations still carry it.
            record.pop("entities", None)
        with closing(sqlite3.connect(path / "metadata.db")) as connection:
            documents = [
                DocumentRecord.model_validate_json(row[0])
                for row in connection.execute("SELECT data FROM documents")
            ]
            parents = [
                ParentChunk.model_validate_json(row[0])
                for row in connection.execute("SELECT data FROM parents")
            ]
        view_store, view_model = None, None
        if (path / "views/manifest.json").exists():
            view_manifest = json.loads(
                (path / "views/manifest.json").read_text(encoding="utf-8")
            )
            view_store = self.store_factory.load(path / "views")
            view_model = view_manifest["embedding_model"]
            if (
                view_manifest["count"] != len(view_store.records)
                or store.dimension != view_store.dimension
            ):
                raise IndexIntegrityError("Invalid auxiliary index manifest or dimension")
        sparse_path = path / "sparse.json"
        sparse = (
            SparseRetriever(
                store.records,
                payload=json.loads(sparse_path.read_text(encoding="utf-8")),
            )
            if sparse_path.exists()
            else None
        )
        snapshot = IndexSnapshot(
            store, documents, parents, view_store, view_model, sparse=sparse
        )
        if manifest is not None:
            snapshot.embedding_cache_keys = manifest.get("embedding_cache_keys", [])
        self._validate_snapshot(snapshot)
        if manifest is None and (
            any(document.version_id for document in documents)
            or (
                expected_signature is not None
                and expected_signature.get("version", 0) >= 6
            )
        ):
            raise IndexIntegrityError("Managed generation is missing its manifest")
        if manifest is not None:
            if "view_assets" in manifest and manifest["view_assets"] != self._view_refs(
                snapshot
            ):
                raise IndexIntegrityError("View provenance differs from its manifest")
            counts = dict(
                documents=len(documents),
                parents=len(parents),
                children=len(store.records),
            )
            if (
                counts != manifest["counts"]
                or self._document_refs(snapshot) != manifest["documents"]
            ):
                raise IndexIntegrityError("Generation manifest does not match its metadata")
        return snapshot

    @staticmethod
    def _document_refs(snapshot):
        return [
            dict(
                document_id=doc.document_id,
                version_id=doc.version_id,
                artifact_id=doc.artifact_id,
                content_hash=doc.checksum,
                processing_signature=doc.processing_signature,
            )
            for doc in sorted(
                snapshot.documents, key=lambda document: document.document_id
            )
        ]

    @staticmethod
    def _view_refs(snapshot):
        if snapshot.view_store is None:
            return []
        sources = {r["chunk_id"]: r for r in snapshot.store.records}
        grouped = {}
        for view in snapshot.view_store.records:
            source = sources[view["source_child_id"]]
            key = source["document_id"]
            item = grouped.setdefault(
                key,
                {
                    "document_id": key,
                    "version_id": source.get("version_id"),
                    "artifact_id": source.get("artifact_id"),
                    "count": 0,
                    "generator_versions": set(),
                },
            )
            item["count"] += 1
            item["generator_versions"].add(view["generator_version"])
        return [
            dict(item, generator_versions=sorted(item["generator_versions"]))
            for _, item in sorted(grouped.items())
        ]

    @staticmethod
    def _validate_snapshot(snapshot):
        documents = {doc.document_id: doc for doc in snapshot.documents}
        parents = {parent.parent_id: parent for parent in snapshot.parents}
        if len(documents) != len(snapshot.documents) or len(parents) != len(
            snapshot.parents
        ):
            raise IndexIntegrityError("Duplicate document or parent identity")
        for document in snapshot.documents:
            if document.version_id and (
                not document.artifact_id or not document.source_blob_path
            ):
                raise IndexIntegrityError(
                    "Managed document is missing its artifact or immutable source reference"
                )
        for parent in snapshot.parents:
            document = documents.get(parent.document_id)
            if document is None:
                raise IndexIntegrityError("Parent has no document")
            if document.version_id and (
                parent.version_id != document.version_id
                or parent.artifact_id != document.artifact_id
                or parent.source_checksum != document.checksum
            ):
                raise IndexIntegrityError(
                    "Parent belongs to a different document version or artifact"
                )
        identities = set()
        for record in snapshot.store.records:
            parent = parents.get(record["parent_id"])
            if parent is None or record["document_id"] != parent.document_id:
                raise IndexIntegrityError("Child has no matching parent/document")
            if record["chunk_id"] in identities:
                raise IndexIntegrityError("Duplicate child identity")
            identities.add(record["chunk_id"])
            if parent.version_id and (
                record.get("version_id") != parent.version_id
                or record.get("artifact_id") != parent.artifact_id
                or record.get("source_checksum") != parent.source_checksum
            ):
                raise IndexIntegrityError(
                    "Child belongs to a different document version or artifact"
                )

        if snapshot.view_store is not None:
            views = [
                RetrievalView.model_validate(
                    {key: value for key, value in record.items() if key != "chunk_id"}
                )
                for record in snapshot.view_store.records
            ]
            validate_views(views, snapshot.store.records)

    def _read_manifest(self, generation):
        """Verified manifest. Treat the returned dict as read-only: it may be shared."""
        if (
            not isinstance(generation, str)
            or not generation
            or Path(generation).name != generation
            or generation in {".", ".."}
        ):
            raise ValueError("Invalid generation identifier")
        revoked_path = self.root / "revoked.json"
        if revoked_path.exists() and generation in json.loads(
            revoked_path.read_text(encoding="utf-8")
        ):
            raise ValueError("Generation was revoked by a hard purge")
        stamp = self._stamp(generation)
        with self._lock:
            hit = self._manifests.get(generation)
            if stamp is None:
                self._manifests.pop(generation, None)
        if stamp is not None and hit is not None and hit[0] == stamp:
            return hit[1]
        manifest = self._verify_manifest(generation)
        if stamp is not None and manifest is not None:
            with self._lock:
                self._manifests[generation] = (stamp, manifest)
                while len(self._manifests) > self.MANIFEST_CACHE:
                    self._manifests.popitem(last=False)
        return manifest

    def _verify_manifest(self, generation):
        path = self.root / generation
        manifest_path = path / "manifest.json"
        if not manifest_path.exists():
            return None  # Frozen generations predate manifests and remain readable.
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        if manifest["schema_version"] != 1 or manifest["generation_id"] != generation:
            raise IndexIntegrityError("Invalid generation manifest identity or schema")
        required = {"faiss.index", "chunks.jsonl", "metadata.db"}
        if "sparse.json" in manifest["files"]:
            required.add("sparse.json")
        if (
            manifest["signature"].get("version", 0) >= 8
            and "sparse.json" not in required
        ):
            raise IndexIntegrityError("Managed generation is missing its sparse index")
        if (path / "views/manifest.json").exists():
            required.update(
                {"views/faiss.index", "views/chunks.jsonl", "views/manifest.json"}
            )
        if set(manifest["files"]) != required:
            raise IndexIntegrityError("Invalid generation manifest asset list")
        for name, expected in manifest["files"].items():
            if file_checksum(path / name) != expected:
                raise IndexIntegrityError(f"Generation asset checksum mismatch: {name}")
        return manifest

    def load_current(self, signature: dict) -> IndexSnapshot | None:
        pointer = self.root / "current.json"
        if not pointer.exists():
            return None
        current = json.loads(pointer.read_text(encoding="utf-8"))
        if current["signature"] != signature:
            return None
        return self.load_generation(current["generation"], expected_signature=signature)

    def usage(self):
        """Generation count and bytes on disk, for the console. Cheap: no hashing."""
        count, size = 0, 0
        if self.root.exists():
            for path in self.root.iterdir():
                if path.is_dir() and len(path.name) == 32 and not path.is_symlink():
                    count += 1
                    size += sum(
                        f.stat().st_size for f in path.rglob("*") if f.is_file()
                    )
        return {"generations": count, "index_bytes": size}

    def current_pointer(self):
        path = self.root / "current.json"
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else None

    def load_published(self):
        """Recover only committed pointers; orphan build directories are never selected."""
        error = None
        for name in ("current.json", "previous.json"):
            path = self.root / name
            if not path.exists():
                continue
            try:
                pointer = json.loads(path.read_text(encoding="utf-8"))
                return self.load_generation(
                    pointer["generation"], expected_signature=pointer["signature"]
                ), pointer
            except (OSError, ValueError, KeyError, sqlite3.DatabaseError) as exc:
                error = exc
        if error is not None:
            raise IndexIntegrityError("No intact published generation is available") from error
        return None

    def publications(self):
        """Committed publication chain, including rollbacks; never orphan build records."""
        pointer = self.current_pointer()
        identity = pointer.get("publication_id") if pointer else None
        result, seen = [], set()
        while identity:
            if (
                identity in seen
                or len(identity) != 32
                or any(c not in "0123456789abcdef" for c in identity)
            ):
                raise IndexIntegrityError("Invalid publication chain")
            seen.add(identity)
            record = self._publications.get(identity)
            if record is None:
                record = json.loads(
                    (self.root / "publications" / (identity + ".json")).read_text(
                        encoding="utf-8"
                    )
                )
                if record["publication_id"] != identity:
                    raise IndexIntegrityError("Invalid publication record identity")
                self._publications[identity] = record
            item = dict(record)
            item["available"] = (
                self.root / item["generation"] / "manifest.json"
            ).exists()
            result.append(item)
            identity = item["previous_publication_id"]
        return result

    def at(self, timestamp):
        from app.knowledge.versioning import parse_time

        target = parse_time(timestamp)
        for item in self.publications():
            if parse_time(item["published_at"]) <= target:
                if not item["available"]:
                    raise NotPublished(
                        "Requested historical publication was purged or collected"
                    )
                manifest = self._read_manifest(item["generation"])
                return self.load_generation(item["generation"], cached=True), dict(
                    item, signature=manifest["signature"]
                )
        raise NotPublished("No retained publication exists at the requested time")

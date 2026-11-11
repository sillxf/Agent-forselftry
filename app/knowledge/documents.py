"""Document commands; HTTP owns streaming, this service owns durable mutations."""

from pathlib import Path
from uuid import uuid4
from app.ingestion.docling_parser import SUPPORTED_EXTENSIONS
from app.core.serialization import public
from app.core.exceptions import InvalidRequest, NotPublished
from app.knowledge.versioning import restore_version


class DocumentService:
    def __init__(self, workspaces, access, audit):
        self.workspaces, self.access, self.audit = workspaces, access, audit

    def _workspace(self, actor, kb_id):
        self.access.authorize(actor, kb_id, admin=True)
        return self.workspaces.get(kb_id)

    def upload_directory(self, actor, kb_id):
        return self._workspace(actor, kb_id).knowledge_dir

    def upload(self, actor, kb_id, filename, temporary, document_id=None):
        with self.workspaces.maintenance_lock(kb_id):
            runtime = self._workspace(actor, kb_id)
            if (
                not filename
                or len(filename) > 180
                or Path(filename).name != filename
                or any(c in filename for c in "/\\:\x00")
                or any(ord(c) < 32 for c in filename)
            ):
                raise InvalidRequest("Use a plain filename")
            if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
                raise InvalidRequest("Unsupported document type")
            if document_id:
                document = runtime.registry.get_document(str(document_id))
                if document.purged_at or document.deleted_at:
                    raise ValueError("Document is unavailable")
                target = Path(document.source_path)
                if not target.resolve().is_relative_to(runtime.knowledge_dir.resolve()):
                    raise ValueError(
                        "External source is not an upload target; migrate it first"
                    )
                if target.suffix.lower() != Path(filename).suffix.lower():
                    raise InvalidRequest("Document update must retain file type")
            else:
                target = runtime.knowledge_dir / uuid4().hex / filename
            temporary = Path(temporary)
            size = temporary.stat().st_size
            if size == 0:
                raise InvalidRequest("Empty upload")
            with runtime.lifecycle.source_lock:
                target.parent.mkdir(parents=True, exist_ok=True)
                temporary.replace(target)
                record, version = runtime.lifecycle.import_document(target)
            self.audit.audit(
                actor["id"],
                "document_uploaded",
                kb_id,
                document_id=record.document_id,
                bytes=size,
            )
            return public(
                {
                    "document": record.model_dump(),
                    "version": version.model_dump(),
                    "needs_build": True,
                }
            )

    def configure(self, actor, kb_id, document_id, *, metadata=None, view_config=None):
        with self.workspaces.maintenance_lock(kb_id):
            runtime = self._workspace(actor, kb_id)
            if metadata and (
                len(metadata) > 50
                or any(len(k) > 100 or len(v) > 2000 for k, v in metadata.items())
            ):
                raise InvalidRequest("Metadata exceeds limits")
            result = runtime.registry.configure(
                str(document_id), metadata=metadata, view_config=view_config
            )
            self.audit.audit(
                actor["id"], "document_configured", kb_id, document_id=str(document_id)
            )
            return public(result.model_dump())

    def validity(self, actor, kb_id, document_id, **validity):
        with self.workspaces.maintenance_lock(kb_id):
            result = self._workspace(actor, kb_id).registry.set_validity(
                str(document_id), **validity
            )
            self.audit.audit(
                actor["id"], "validity_changed", kb_id, document_id=str(document_id)
            )
            return public(result.model_dump())

    def review(self, actor, kb_id, document_id, review_after):
        with self.workspaces.maintenance_lock(kb_id):
            result = self._workspace(actor, kb_id).registry.set_review_after(
                str(document_id), review_after
            )
            self.audit.audit(
                actor["id"], "review_date_changed", kb_id, document_id=str(document_id)
            )
            return public(result.model_dump())

    def supersede(self, actor, kb_id, document_id, replacement_id):
        with self.workspaces.maintenance_lock(kb_id):
            workspace = self._workspace(actor, kb_id)
            if replacement_id is not None:
                # The old document disappears from search at once; its replacement
                # must already be searchable, or the content would vanish until a build.
                pointer = workspace.repository.current_pointer()
                manifest = (
                    workspace.repository._read_manifest(pointer["generation"])
                    if pointer
                    else None
                )
                published = {d["document_id"] for d in (manifest or {}).get("documents", [])}
                if replacement_id not in published:
                    raise NotPublished(
                        "Build and publish the replacement document before superseding"
                    )
            result = workspace.registry.set_superseded_by(
                str(document_id), replacement_id
            )
            self.audit.audit(
                actor["id"],
                "document_superseded" if replacement_id else "supersede_cleared",
                kb_id,
                document_id=str(document_id),
                replacement_id=replacement_id,
            )
            return public(result.model_dump())

    def deleted(self, actor, kb_id, document_id, value=True):
        with self.workspaces.maintenance_lock(kb_id):
            result = self._workspace(actor, kb_id).registry.set_deleted(
                str(document_id), value
            )
            self.audit.audit(
                actor["id"],
                "document_deleted" if value else "document_restored",
                kb_id,
                document_id=str(document_id),
            )
            return public(result.model_dump())

    def restore(self, actor, kb_id, document_id, version_id):
        with self.workspaces.maintenance_lock(kb_id):
            result = restore_version(
                self._workspace(actor, kb_id), str(document_id), str(version_id)
            )
            self.audit.audit(
                actor["id"], "version_selected", kb_id, document_id=str(document_id)
            )
            return public(result.model_dump())

    def download(self, actor, kb_id, document_id, version_id):
        self.access.authorize(actor, kb_id)
        workspace = self.workspaces.get(kb_id)
        document = workspace.registry.get_document(document_id)
        if document.purged_at or document.deleted_at:
            raise KeyError("Document unavailable")
        version = next(
            (
                v
                for v in workspace.registry.list_versions(document_id)
                if v.version_id == version_id
            ),
            None,
        )
        if version is None:
            raise KeyError("Version not found")
        path = Path(version.source_blob_path)
        if not path.resolve().is_relative_to(
            (workspace.storage_dir / "sources").resolve()
        ):
            raise ValueError("Source is outside the managed root")
        self.audit.audit(
            actor["id"],
            "original_downloaded",
            kb_id,
            document_id=document_id,
            version_id=version_id,
        )
        return path, Path(document.source_path).name

"""Capture immutable source bytes and bind them to explicit processing identities."""
import hashlib
import json
import os
import tempfile
from pathlib import Path

from app.rag.ingestion.docling_parser import SUPPORTED_EXTENSIONS, file_checksum
from app.rag.lifecycle.registry import DocumentRegistry
from app.rag.models import DocumentRecord


class LifecycleService:
    def __init__(self, storage_dir, registry=None):
        self.sources = Path(storage_dir) / "sources"
        self.registry = registry if registry is not None else DocumentRegistry(storage_dir)

    def import_document(self, source_path, *, source_id=None, expected_hash=None):
        """Freeze bytes before registering them. Failed capture never advances the registry."""
        source = Path(source_path).resolve(strict=True)
        if not source.is_file() or source.suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError(f"Unsupported knowledge file: {source.name}")
        self.sources.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            digest = hashlib.sha256()
            with tempfile.NamedTemporaryFile(dir=self.sources, delete=False) as output:
                temporary = Path(output.name)
                with source.open("rb") as stream:
                    for block in iter(lambda: stream.read(1024 * 1024), b""):
                        digest.update(block)
                        output.write(block)
                output.flush()
                os.fsync(output.fileno())
            content_hash = digest.hexdigest()
            if expected_hash is not None and content_hash != expected_hash:
                raise ValueError(f"Source changed during build: {source.name}")
            blob = self.sources / content_hash / ("source" + source.suffix.lower())
            blob.parent.mkdir(parents=True, exist_ok=True)
            try:
                # A complete file becomes visible at once; never replace an existing blob.
                os.link(temporary, blob)
            except FileExistsError:
                if file_checksum(blob) != content_hash:
                    raise ValueError(f"Immutable source blob is corrupt: {content_hash}")
            return self.registry.register_source(source, content_hash, blob.resolve(), source.suffix.lower().lstrip("."),
                                                 source_id=source_id)
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @staticmethod
    def processing_document(document, version, processing_signature):
        # The filename is embedded in search_text, so a rename changes derived assets,
        # not content identity. JSON, not repr(), makes the fingerprint reproducible.
        filename = Path(document.source_path).name
        identity = json.dumps([version.version_id, processing_signature, filename],
                              ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        return DocumentRecord(
            document_id=document.document_id, filename=filename, file_type=version.file_type,
            source_path=document.source_path, checksum=version.content_hash, version=version.version_id,
            version_id=version.version_id, artifact_id=hashlib.sha256(identity.encode("utf-8")).hexdigest(),
            source_blob_path=version.source_blob_path, processing_signature=processing_signature,
        )

    def rename(self, document_id, new_path):
        document = self.registry.get_document(document_id)
        version = next(v for v in self.registry.list_versions(document_id) if v.version_id == document.latest_version_id)
        path = Path(new_path).resolve(strict=True)
        if path.suffix.lower().lstrip(".") != version.file_type or file_checksum(path) != version.content_hash:
            raise ValueError("Rename requires the same content and file type; import content changes separately")
        return self.registry.rename(document_id, path)


    def delete(self, document_id):
        return self.registry.set_deleted(document_id)

    def restore(self, document_id):
        return self.registry.set_deleted(document_id, False)

    def set_validity(self, document_id, *, effective_at=None, expires_at=None):
        return self.registry.set_validity(document_id, effective_at=effective_at, expires_at=expires_at)

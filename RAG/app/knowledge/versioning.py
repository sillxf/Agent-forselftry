"""Explicit version activation and read-only publication-time retrieval."""

from datetime import datetime, timezone
from pathlib import Path
from filelock import FileLock

from app.ingestion.docling_parser import file_checksum
from app.core.exceptions import IndexIntegrityError, InvalidRequest


def parse_time(value):
    try:
        parsed = (
            datetime.fromisoformat(value.replace("Z", "+00:00"))
            if isinstance(value, str)
            else value
        )
    except ValueError as exc:
        raise InvalidRequest("Timestamps must be ISO 8601 with a timezone") from exc
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise InvalidRequest("Historical timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def restore_version(retriever, document_id, version_id):
    """Pin immutable bytes, without overwriting a user's external source file.

    An explicit subsequent source content change/import supersedes this pin. A rebuild
    publishes the activation; old records and previously published history are immutable.
    """
    with FileLock(str(retriever.storage_dir / "build.lock"), timeout=0):
        version = next(
            (
                v
                for v in retriever.registry.list_versions(document_id)
                if v.version_id == version_id
            ),
            None,
        )
        if version is None:
            raise KeyError(version_id)
        if file_checksum(Path(version.source_blob_path)) != version.content_hash:
            raise IndexIntegrityError("Historical source blob is missing or corrupt")
        document = retriever.registry.select_version(document_id, version_id)
    return document

"""Explicit version activation and read-only publication-time retrieval."""

from datetime import datetime, timezone
from pathlib import Path

from rag_service.core.ingestion.docling_parser import file_checksum


def parse_time(value):
    parsed = (
        datetime.fromisoformat(value.replace("Z", "+00:00"))
        if isinstance(value, str)
        else value
    )
    if parsed.tzinfo is None or parsed.utcoffset() is None:
        raise ValueError("Historical timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def restore_version(retriever, document_id, version_id):
    """Pin immutable bytes, without overwriting a user's external source file.

    An explicit subsequent source content change/import supersedes this pin. A rebuild
    publishes the activation; old records and previously published history are immutable.
    """
    with retriever.build_service.lock:
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
            raise ValueError("Historical source blob is missing or corrupt")
        document = retriever.registry.select_version(document_id, version_id)
    return document


class HistoricalRetriever:
    def __init__(self, owner, snapshot, publication, at):
        self.orchestrator = owner.orchestrator
        self.pipeline = owner._prepare_pipeline(
            snapshot.store,
            {p.parent_id: p for p in snapshot.parents},
            publication["signature"]["model"],
            **owner._view_options(snapshot),
        )
        self.pipeline.generation_id = publication["generation"]
        moment = parse_time(at)
        documents = snapshot.documents
        if any(d.lifecycle_state is None for d in documents):
            raise ValueError("This generation predates historical lifecycle recording")

        def eligible():
            # Read the authoritative registry, fail closed if it is unavailable.
            owner.registry.eligible_ids(d.document_id for d in documents)
            purged = owner.registry.purged_ids()
            return {
                d.document_id
                for d in documents
                if d.document_id not in purged
                and not d.lifecycle_state.get("deleted_at")
                and (
                    not d.lifecycle_state.get("effective_at")
                    or parse_time(d.lifecycle_state["effective_at"]) <= moment
                )
                and (
                    not d.lifecycle_state.get("expires_at")
                    or moment < parse_time(d.lifecycle_state["expires_at"])
                )
            }

        self.pipeline.eligibility = eligible

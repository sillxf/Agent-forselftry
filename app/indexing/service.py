"""Explicit build/publication operations and durable job submission."""

import json
from app.core.contracts import IndexBuildConfig, JobRequest
from app.core.serialization import public
from app.ingestion.docling_parser import DoclingParser
from app.indexing.builder import IndexBuilder


class IndexingService:
    def __init__(
        self,
        root,
        jobs,
        bases,
        models,
        workspaces,
        providers,
        factory,
        access,
        audit,
        parser_factory=None,
    ):
        self.root, self.jobs, self.bases, self.models = root, jobs, bases, models
        self.workspaces, self.providers, self.factory = workspaces, providers, factory
        self.access, self.audit, self.parser_factory = access, audit, parser_factory

    def submit(self, actor, kb_id, request, *, idempotency=None):
        configuration = self.access.authorize(actor, kb_id, admin=True)
        if request.operation == "build":
            self.models.model(
                configuration["build"]["embedding_id"], require_enabled=True
            )
        if request.operation == "purge":
            raise ValueError(
                "Use DELETE /knowledge-bases/{kb_id}/documents/{document_id}?confirm=true; deletion runs immediately"
            )
        payload = dict(request.model_dump(), configuration=configuration)
        job = self.jobs.enqueue(kb_id, request.operation, payload, idempotency)
        self.audit.audit(
            actor["id"],
            "job_submitted",
            kb_id,
            job_id=job["id"],
            operation=request.operation,
        )
        return job

    def list(self, actor):
        self.access.authorize(actor, admin=True)
        rows = public(self.jobs.jobs())
        marker = self.root / "desktop-worker-cutoff"
        cutoff = float(marker.read_text(encoding="ascii")) if marker.exists() else None
        for job in rows:
            job["awaiting_confirmation"] = bool(
                cutoff is not None
                and job["status"] == "queued"
                and job["updated"] < cutoff
            )
        return rows

    def retry(self, actor, job_id):
        self.access.authorize(actor, admin=True)
        old = self.jobs.job(job_id)
        marker = self.root / "desktop-worker-cutoff"
        if (
            old["status"] == "queued"
            and old["operation"] != "purge"
            and marker.exists()
            and old["updated"] < float(marker.read_text(encoding="ascii"))
        ):
            self.access.authorize(actor, old["kb_id"], admin=True)
            return self.jobs.confirm_queued(job_id)
        if old["status"] not in {"failed", "interrupted"}:
            raise ValueError("Only failed/interrupted jobs may be retried")
        payload = json.loads(old["payload"])
        request = JobRequest.model_validate(
            {key: value for key, value in payload.items() if key != "configuration"}
        )
        return self.submit(actor, old["kb_id"], request)

    def delete_document(self, actor, kb_id, document_id):
        with self.workspaces.maintenance_lock(kb_id):
            from app.knowledge.purge import purge_document

            self.access.authorize(actor, kb_id, admin=True)
            result = purge_document(self.workspaces.get(kb_id), document_id)
            self.jobs.complete_pending_purges(kb_id, document_id, result)
            self.audit.audit(
                actor["id"], "document_purged", kb_id, document_id=document_id
            )
            return result

    def execute(self, job, payload):
        with self.workspaces.maintenance_lock(job["kb_id"]):
            workspace = self.workspaces.get(job["kb_id"])
            if job["operation"] == "purge":
                # Existing queues remain resumable without initializing a parser/model.
                from app.knowledge.purge import purge_document

                return purge_document(workspace, payload["document_id"])
            configuration = IndexBuildConfig.model_validate(
                payload["configuration"]["build"]
            )
            parser = (
                self.parser_factory(workspace, configuration)
                if self.parser_factory
                else DoclingParser(
                    archive_dir=workspace.storage_dir / "parsed",
                    image_dir=workspace.storage_dir / "images",
                    ocr_enabled=configuration.ocr_enabled,
                )
            )
            builder = IndexBuilder(
                workspace,
                configuration,
                parser,
                self.providers.embedding,
                self.factory,
                progress=lambda stage: self.jobs.progress(job["id"], stage),
                publication_guard=lambda: self.jobs.build_guard(
                    job["kb_id"], payload["configuration"]["build"]
                ),
            )
            operation = job["operation"]
            if operation == "build":
                return {
                    "core_job_id": builder.run(full=payload["full"]),
                    "metrics": builder.last_build_metrics,
                    "current": workspace.repository.current_pointer(),
                }
            if operation == "rollback":
                return {
                    "core_job_id": builder.rollback(payload["generation_id"]),
                    "current": workspace.repository.current_pointer(),
                }
            if operation == "gc":
                from app.indexing.garbage_collector import collect_generations

                return collect_generations(builder)
            raise ValueError("Unsupported job operation")

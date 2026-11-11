"""Single durable worker. Restarts mark uncertain tasks interrupted, never blindly replay paid work."""

import json, logging, time
from filelock import FileLock
from rag_service.providers import usage_context


class Worker:
    def __init__(self, service):
        self.service = service
        self.catalog = service.catalog

    def run_once(self):
        job = self.catalog.claim()
        if job is None:
            return False
        usage = []
        context = usage_context.set(usage)
        try:
            payload = json.loads(job["payload"])
            r = self.service.runtime(
                job["kb_id"], configuration=payload["configuration"]
            )
            r.publication_guard = lambda: self.catalog.build_guard(
                job["kb_id"], payload["configuration"]["build"]
            )
            r.progress = lambda stage: self.catalog.progress(job["id"], stage)
            operation = job["operation"]
            if operation == "build":
                result = {
                    "core_job_id": r.build_index(full=payload["full"]),
                    "metrics": r.last_build_metrics,
                    "current": r.repository.current_pointer(),
                }
            elif operation == "rollback":
                result = {
                    "core_job_id": r.rollback_generation(payload["generation_id"]),
                    "current": r.repository.current_pointer(),
                }
            elif operation == "purge":
                result = r.purge_document(payload["document_id"])
            elif operation == "gc":
                from rag_service.core.indexing.maintenance import collect_generations

                result = collect_generations(r.build_service)
            else:
                raise ValueError("Unsupported job operation")
            self.catalog.finish(
                job["id"], result=dict(output=result, model_usage=usage)
            )
            self.catalog.audit(
                "worker",
                "job_completed",
                job["kb_id"],
                job_id=job["id"],
                operation=operation,
                usage=usage,
            )
        except Exception as exc:
            logging.exception("Job %s failed", job["id"])
            # Provider HTTP exceptions may contain URLs/keys: public errors are categorical.
            self.catalog.finish(
                job["id"],
                error=type(exc).__name__
                + ": operation failed; inspect server log and retry explicitly",
            )
            self.catalog.audit(
                "worker",
                "job_failed",
                job["kb_id"],
                job_id=job["id"],
                error_type=type(exc).__name__,
                usage=usage,
            )
        finally:
            usage_context.reset(context)
        return True

    def run(self, *, once=False):
        with FileLock(str(self.catalog.root / "worker.lock"), timeout=0):
            self.catalog.recover()
            while True:
                if not self.run_once():
                    if once:
                        break
                    time.sleep(1)

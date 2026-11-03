"""Single durable worker. Restarts mark uncertain tasks interrupted, never blindly replay paid work."""

import json, logging, time
from filelock import FileLock
from app.models.pool import usage_context


class Worker:
    def __init__(self, indexing):
        self.indexing = indexing
        self.jobs = indexing.jobs
        self.audit = indexing.audit

    def run_once(self):
        job = self.jobs.claim()
        if job is None:
            return False
        usage = []
        context = usage_context.set(usage)
        try:
            payload = json.loads(job["payload"])
            operation = job["operation"]
            result = self.indexing.execute(job, payload)
            self.jobs.finish(job["id"], result=dict(output=result, model_usage=usage))
            self.audit.audit(
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
            self.jobs.finish(
                job["id"],
                error=type(exc).__name__
                + ": operation failed; inspect server log and retry explicitly",
            )
            self.audit.audit(
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
        with FileLock(str(self.indexing.root / "worker.lock"), timeout=0):
            self.jobs.recover()
            while True:
                if not self.run_once():
                    if once:
                        break
                    time.sleep(1)

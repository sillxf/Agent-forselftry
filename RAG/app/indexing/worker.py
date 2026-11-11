"""Single durable worker. Restarts mark uncertain tasks interrupted, never blindly replay paid work."""

import json, logging, time
from filelock import FileLock
from app.indexing.repository import JobCancelled
from app.models.pool import usage_context


class Worker:
    def __init__(self, indexing):
        self.indexing = indexing
        self.jobs = indexing.jobs
        self.audit = indexing.audit

    def run_once(self, *, skip_legacy_purge=False, confirmed_after=None):
        job = self.jobs.claim(
            skip_legacy_purge=skip_legacy_purge, confirmed_after=confirmed_after
        )
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
        except JobCancelled:
            self.jobs.finish(job["id"], cancelled=True)
            self.audit.audit(
                "worker", "job_cancelled", job["kb_id"], job_id=job["id"], operation=operation
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

    def run(self, *, once=False, desktop_safe_start=False):
        with FileLock(str(self.indexing.root / "worker.lock"), timeout=0):
            self.jobs.recover()
            cutoff = None
            if desktop_safe_start:
                marker = self.indexing.root / "desktop-worker-cutoff"
                if not marker.exists():
                    marker.write_text(str(time.time()), encoding="ascii")
                cutoff = float(marker.read_text(encoding="ascii"))
                self.jobs.hold_legacy_purges()
                (self.indexing.root / "desktop-worker-ready").write_text(
                    "1", encoding="ascii"
                )
            while True:
                if not self.run_once(
                    skip_legacy_purge=desktop_safe_start, confirmed_after=cutoff
                ):
                    if once:
                        break
                    time.sleep(1)

"""Durable jobs and optimistic publication guard."""

from contextlib import contextmanager
import json, time
from uuid import uuid4


class JobRepository:
    def __init__(self, connect, knowledge_base):
        self.connect, self.kb = connect, knowledge_base

    def enqueue(self, kb_id, operation, payload, idempotency=None):
        self.kb(kb_id)
        identity = uuid4().hex
        now = time.time()
        encoded = json.dumps(payload, sort_keys=True)
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            self.kb(
                kb_id
            )  # Recheck under the write transaction; deletion cannot race enqueue.
            if idempotency:
                old = c.execute(
                    "SELECT * FROM jobs WHERE idempotency=?", (idempotency,)
                ).fetchone()
                if old:
                    if (old["kb_id"], old["operation"], old["payload"]) != (
                        kb_id,
                        operation,
                        encoded,
                    ):
                        raise ValueError(
                            "Idempotency key was used for different inputs"
                        )
                    return dict(old)
            c.execute(
                "INSERT INTO jobs VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                (
                    identity,
                    kb_id,
                    operation,
                    encoded,
                    "queued",
                    "queued",
                    now,
                    now,
                    None,
                    None,
                    idempotency,
                ),
            )
        return self.job(identity)

    def delete_for_base(self, kb_id):
        with self.connect() as c:
            c.execute("DELETE FROM jobs WHERE kb_id=?", (kb_id,))

    def complete_pending_purges(self, kb_id, document_id, result):
        """Retire only still-queued duplicates of a completed direct deletion."""
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            rows = c.execute(
                "SELECT id,payload FROM jobs WHERE kb_id=? AND operation='purge' AND status='queued'",
                (kb_id,),
            ).fetchall()
            for row in rows:
                if json.loads(row["payload"]).get("document_id") == document_id:
                    c.execute(
                        "UPDATE jobs SET status='succeeded',stage='completed',result=?,error=NULL,updated=? WHERE id=?",
                        (
                            json.dumps({"output": result, "completed_directly": True}),
                            time.time(),
                            row["id"],
                        ),
                    )

    def job(self, identity):
        with self.connect() as c:
            row = c.execute("SELECT * FROM jobs WHERE id=?", (identity,)).fetchone()
        if row is None:
            raise KeyError("Job not found")
        return dict(row)

    def jobs(self, kb_id=None):
        with self.connect() as c:
            return [
                dict(r)
                for r in c.execute(
                    "SELECT * FROM jobs WHERE (? IS NULL OR kb_id=?) ORDER BY created DESC LIMIT 100",
                    (kb_id, kb_id),
                )
            ]

    def recover(self):
        with self.connect() as c:
            c.execute(
                "UPDATE jobs SET status='interrupted',stage='interrupted',error='Worker stopped; inspect publication/purge state, then explicitly retry',updated=? WHERE status='running'",
                (time.time(),),
            )

    def claim(self):
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute(
                "SELECT * FROM jobs WHERE status='queued' ORDER BY created LIMIT 1"
            ).fetchone()
            if not row:
                return None
            c.execute(
                "UPDATE jobs SET status='running',stage='starting',updated=? WHERE id=?",
                (time.time(), row["id"]),
            )
            return dict(row)

    def progress(self, identity, stage):
        with self.connect() as c:
            c.execute(
                "UPDATE jobs SET stage=?,updated=? WHERE id=?",
                (stage, time.time(), identity),
            )

    def finish(self, identity, *, result=None, error=None):
        with self.connect() as c:
            c.execute(
                "UPDATE jobs SET status=?,stage=?,result=?,error=?,updated=? WHERE id=?",
                (
                    "failed" if error else "succeeded",
                    "failed" if error else "completed",
                    json.dumps(result),
                    error,
                    time.time(),
                    identity,
                ),
            )

    @contextmanager
    def build_guard(self, kb_id, expected_build):
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute(
                "SELECT data FROM knowledge_bases WHERE id=?", (kb_id,)
            ).fetchone()
            if row is None or json.loads(row[0])["build"] != expected_build:
                raise ValueError(
                    "Build configuration changed; obsolete generation was not published"
                )
            yield

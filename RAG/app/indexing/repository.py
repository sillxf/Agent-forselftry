"""Durable jobs and optimistic publication guard."""

import json
import time
from contextlib import contextmanager
from uuid import uuid4


class JobCancelled(Exception):
    """Raised at a safe checkpoint after a user cancels a task."""


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
                "INSERT INTO jobs (id,kb_id,operation,payload,status,stage,created,updated,error,result,idempotency) VALUES (?,?,?,?,?,?,?,?,?,?,?)",
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
        """Retire unfinished legacy purge jobs after a successful direct deletion."""
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            rows = c.execute(
                "SELECT id,payload FROM jobs WHERE kb_id=? AND operation='purge' AND status IN ('queued','interrupted','failed')",
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
                "UPDATE jobs SET status='interrupted',stage='interrupted',control_request=NULL,error='Worker stopped; inspect publication state, then explicitly retry',updated=? WHERE status IN ('running','publishing')",
                (time.time(),),
            )
            # A live in-memory build cannot be resumed after its worker exits.
            c.execute(
                "UPDATE jobs SET status='interrupted',stage='interrupted',control_request=NULL,error='Worker stopped while paused; explicitly retry to start a fresh build',updated=? WHERE status='paused' AND stage='paused'",
                (time.time(),),
            )

    def hold_legacy_purges(self):
        with self.connect() as c:
            return c.execute(
                "UPDATE jobs SET status='interrupted',stage='interrupted',error=?,updated=? WHERE operation='purge' AND status='queued'",
                ("历史删除任务未执行。请到文档页核对后直接删除。", time.time()),
            ).rowcount

    def claim(self, *, skip_legacy_purge=False, confirmed_after=None):
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute(
                "SELECT * FROM jobs WHERE status='queued' AND (?=0 OR operation!='purge') AND (? IS NULL OR updated>=?) ORDER BY created LIMIT 1",
                (skip_legacy_purge, confirmed_after, confirmed_after),
            ).fetchone()
            if not row:
                return None
            c.execute(
                "UPDATE jobs SET status='running',stage='starting',updated=? WHERE id=?",
                (time.time(), row["id"]),
            )
            return dict(row)

    def confirm_queued(self, identity):
        with self.connect() as c:
            c.execute(
                "UPDATE jobs SET updated=? WHERE id=? AND status='queued'",
                (time.time(), identity),
            )
        return self.job(identity)

    def control(self, identity, action):
        if action not in {"pause", "resume", "cancel"}:
            raise ValueError("Unsupported job control action")
        now = time.time()
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            row = c.execute("SELECT * FROM jobs WHERE id=?", (identity,)).fetchone()
            if row is None:
                raise KeyError("Job not found")
            status, stage = row["status"], row["stage"]
            control_request = row["control_request"]

            if action == "cancel":
                if status == "queued" or (status == "paused" and stage == "paused_queued"):
                    c.execute(
                        "UPDATE jobs SET status='cancelled',stage='cancelled',updated=? WHERE id=?",
                        (now, identity),
                    )
                elif status in {"running", "paused"}:
                    if status == "running" and stage == "publishing":
                        raise ValueError("任务已进入最后发布步骤，不能再取消")
                    c.execute(
                        "UPDATE jobs SET control_request='cancel',stage='cancelling',updated=? WHERE id=?",
                        (now, identity),
                    )
                elif status != "cancelled":
                    raise ValueError("只有排队中或执行中的任务可以取消")
            elif action == "pause":
                if status == "queued":
                    c.execute(
                        "UPDATE jobs SET status='paused',stage='paused_queued',updated=? WHERE id=?",
                        (now, identity),
                    )
                elif status == "running":
                    if stage == "publishing":
                        raise ValueError("任务已进入最后发布步骤，不能再暂停")
                    if control_request == "cancel":
                        raise ValueError("任务正在取消")
                    c.execute(
                        "UPDATE jobs SET control_request='pause',stage='pause_requested',updated=? WHERE id=?",
                        (now, identity),
                    )
                elif status != "paused":
                    raise ValueError("只有排队中或执行中的任务可以暂停")
            else:  # resume
                if status == "paused" and stage == "paused_queued":
                    c.execute(
                        "UPDATE jobs SET status='queued',stage='queued',updated=? WHERE id=?",
                        (now, identity),
                    )
                elif status == "paused" and control_request == "pause":
                    c.execute(
                        "UPDATE jobs SET status='running',control_request=NULL,updated=? WHERE id=?",
                        (now, identity),
                    )
                elif status == "running" and control_request == "pause":
                    # Resume quickly even if the worker has not reached the pause checkpoint.
                    c.execute(
                        "UPDATE jobs SET control_request=NULL,updated=? WHERE id=?",
                        (now, identity),
                    )
                else:
                    raise ValueError("任务当前不在暂停状态")
        return self.job(identity)

    def checkpoint(self, identity, *, stage=None, poll_seconds=0.5):
        """Update progress and honor pause/cancel requests between expensive steps."""
        while True:
            with self.connect() as c:
                c.execute("BEGIN IMMEDIATE")
                row = c.execute(
                    "SELECT status,control_request FROM jobs WHERE id=?", (identity,)
                ).fetchone()
                if row is None:
                    raise JobCancelled("任务已不存在")
                if row["status"] == "cancelled" or row["control_request"] == "cancel":
                    raise JobCancelled("用户已取消任务")
                if row["status"] == "interrupted":
                    raise JobCancelled("任务已中断")
                if row["status"] == "paused" or row["control_request"] == "pause":
                    if row["status"] == "running":
                        c.execute(
                            "UPDATE jobs SET status='paused',stage='paused',updated=? WHERE id=? AND status='running'",
                            (time.time(), identity),
                        )
                    should_wait = True
                elif row["status"] == "running":
                    if stage:
                        c.execute(
                            "UPDATE jobs SET stage=?,updated=? WHERE id=? AND status='running'",
                            (stage, time.time(), identity),
                        )
                    should_wait = False
                else:
                    raise JobCancelled("任务不再处于执行状态")
            if not should_wait:
                return
            time.sleep(poll_seconds)

    def progress(self, identity, stage):
        self.checkpoint(identity, stage=stage)

    @contextmanager
    def publish_guard(self, identity, kb_id, expected_build):
        """Validate the job and make the final pointer switch non-cancellable."""
        while True:
            wait = False
            with self.connect() as c:
                c.execute("BEGIN IMMEDIATE")
                row = c.execute(
                    "SELECT status,control_request FROM jobs WHERE id=?", (identity,)
                ).fetchone()
                if row is None:
                    raise JobCancelled("任务已不存在")
                if row["control_request"] == "cancel":
                    raise JobCancelled("用户已取消任务")
                if row["status"] == "paused" or row["control_request"] == "pause":
                    wait = True
                elif row["status"] != "running":
                    raise ValueError("任务不在执行状态，不能发布")
                else:
                    base = c.execute(
                        "SELECT data FROM knowledge_bases WHERE id=?", (kb_id,)
                    ).fetchone()
                    if base is None or json.loads(base["data"])["build"] != expected_build:
                        raise ValueError(
                            "Build configuration changed; obsolete generation was not published"
                        )
                    c.execute(
                        "UPDATE jobs SET stage='publishing',updated=? WHERE id=?",
                        (time.time(), identity),
                    )
                    yield
                    return
            if wait:
                time.sleep(0.5)

    def finish(self, identity, *, result=None, error=None, cancelled=False):
        with self.connect() as c:
            c.execute(
                "UPDATE jobs SET status=?,stage=?,result=?,error=?,control_request=NULL,updated=? WHERE id=?",
                (
                    "cancelled" if cancelled else "failed" if error else "succeeded",
                    "cancelled" if cancelled else "failed" if error else "completed",
                    json.dumps(result),
                    "任务已取消；未发布新版本，已完成的清理不会回滚" if cancelled else error,
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

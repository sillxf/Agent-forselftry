"""Bounded audit persistence; callers supply hashes/statistics, not query bodies."""

import json, time
from threading import Lock

RETENTION_SECONDS = 30 * 86400
PRUNE_INTERVAL_SECONDS = 60


class AuditRepository:
    def __init__(self, connect):
        self.connect = connect
        self._pruned_at = 0.0
        self._lock = Lock()

    def audit(self, actor, action, kb_id=None, **details):
        now = time.time()
        with self._lock:
            # Pruning on every search scanned the table each time; once a minute
            # per process keeps it bounded at a fraction of the cost.
            prune = now - self._pruned_at >= PRUNE_INTERVAL_SECONDS
            if prune:
                self._pruned_at = now
        with self.connect() as c:
            c.execute(
                "INSERT INTO audit(at,actor,action,kb_id,details) VALUES (?,?,?,?,?)",
                (now, actor, action, kb_id, json.dumps(details)),
            )
            if prune:
                c.execute("DELETE FROM audit WHERE at<?", (now - RETENTION_SECONDS,))

    def audits(self):
        with self.connect() as c:
            return [
                dict(r)
                for r in c.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 200")
            ]

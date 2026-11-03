"""Bounded audit persistence; callers supply hashes/statistics, not query bodies."""

import json, time


class AuditRepository:
    def __init__(self, connect):
        self.connect = connect

    def audit(self, actor, action, kb_id=None, **details):
        with self.connect() as c:
            c.execute(
                "INSERT INTO audit(at,actor,action,kb_id,details) VALUES (?,?,?,?,?)",
                (time.time(), actor, action, kb_id, json.dumps(details)),
            )
            c.execute("DELETE FROM audit WHERE at<?", (time.time() - 30 * 86400,))

    def audits(self):
        with self.connect() as c:
            return [
                dict(r)
                for r in c.execute("SELECT * FROM audit ORDER BY id DESC LIMIT 200")
            ]

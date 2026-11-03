"""Hashed, scoped, revocable keys and atomic search quotas."""

import hashlib, hmac, json, secrets, time
from uuid import uuid4


class KeyRepository:
    def __init__(self, connect, knowledge_base):
        self.connect, self.kb = connect, knowledge_base

    def create_key(self, value):
        identity = uuid4().hex
        token = "rag_" + identity + "." + secrets.token_urlsafe(32)
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            for kb in value.knowledge_base_ids:
                self.kb(kb)
            c.execute(
                "INSERT INTO api_keys(id,name,digest,scopes,rpm) VALUES (?,?,?,?,?)",
                (
                    identity,
                    value.name,
                    hashlib.sha256(token.encode()).hexdigest(),
                    json.dumps(value.knowledge_base_ids),
                    value.requests_per_minute,
                ),
            )
        return dict(id=identity, token=token)

    def authenticate(self, token):
        identity = token.removeprefix("rag_").split(".")[0]
        with self.connect() as c:
            row = c.execute(
                "SELECT * FROM api_keys WHERE id=? AND revoked=0", (identity,)
            ).fetchone()
        if row is None or not hmac.compare_digest(
            row["digest"], hashlib.sha256(token.encode()).hexdigest()
        ):
            return None
        return dict(
            id=identity, scopes=json.loads(row["scopes"]), rpm=row["rpm"], admin=False
        )

    def reserve(self, actor):
        if actor["admin"]:
            return
        minute = int(time.time() // 60)
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            c.execute(
                "INSERT INTO quota VALUES (?,?,0) ON CONFLICT DO NOTHING",
                (actor["id"], minute),
            )
            used = c.execute(
                "SELECT used FROM quota WHERE key_id=? AND minute=?",
                (actor["id"], minute),
            ).fetchone()[0]
            if used >= actor["rpm"]:
                raise PermissionError("Rate limit exceeded")
            c.execute(
                "UPDATE quota SET used=used+1 WHERE key_id=? AND minute=?",
                (actor["id"], minute),
            )
            c.execute("DELETE FROM quota WHERE minute<?", (minute - 2,))

    def keys(self):
        with self.connect() as c:
            return [
                dict(
                    id=r["id"],
                    name=r["name"],
                    knowledge_base_ids=json.loads(r["scopes"]),
                    requests_per_minute=r["rpm"],
                    revoked=bool(r["revoked"]),
                )
                for r in c.execute("SELECT * FROM api_keys")
            ]

    def revoke(self, identity):
        with self.connect() as c:
            c.execute("UPDATE api_keys SET revoked=1 WHERE id=?", (identity,))

    def remove_scope(self, kb_id):
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
            for row in c.execute("SELECT id,scopes FROM api_keys").fetchall():
                scopes = json.loads(row["scopes"])
                if kb_id not in scopes:
                    continue
                scopes = [scope for scope in scopes if scope != kb_id]
                c.execute(
                    "UPDATE api_keys SET scopes=?,revoked=CASE WHEN ? THEN revoked ELSE 1 END WHERE id=?",
                    (json.dumps(scopes), bool(scopes), row["id"]),
                )
                if not scopes:
                    c.execute("DELETE FROM quota WHERE key_id=?", (row["id"],))

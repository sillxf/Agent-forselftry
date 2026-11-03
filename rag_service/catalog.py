"""Small durable control plane. Knowledge contents stay in isolated per-KB registries."""

from contextlib import contextmanager
from pathlib import Path
import hashlib, hmac, json, secrets, sqlite3, time
from uuid import uuid4
from rag_service.contracts import KnowledgeBaseCreate, ModelConfig

SCHEMA = """
CREATE TABLE IF NOT EXISTS knowledge_bases(id TEXT PRIMARY KEY, data TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS models(id TEXT PRIMARY KEY, config TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1);
CREATE TABLE IF NOT EXISTS api_keys(id TEXT PRIMARY KEY, name TEXT NOT NULL, digest TEXT NOT NULL, scopes TEXT NOT NULL, rpm INTEGER NOT NULL, revoked INTEGER NOT NULL DEFAULT 0);
CREATE TABLE IF NOT EXISTS quota(key_id TEXT NOT NULL, minute INTEGER NOT NULL, used INTEGER NOT NULL, PRIMARY KEY(key_id,minute));
CREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,kb_id TEXT NOT NULL,operation TEXT NOT NULL,payload TEXT NOT NULL,status TEXT NOT NULL,stage TEXT NOT NULL,created REAL NOT NULL,updated REAL NOT NULL,error TEXT,result TEXT,idempotency TEXT UNIQUE);
CREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,at REAL NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,kb_id TEXT,details TEXT NOT NULL);
"""


class Catalog:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "catalog.sqlite3"
        with self.connect() as c:
            version = c.execute("PRAGMA user_version").fetchone()[0]
            if version not in {0, 1}:
                raise ValueError(
                    "Unsupported catalog schema; restore matching code/data"
                )
            c.executescript(SCHEMA)
            c.execute("PRAGMA user_version=1")

    @contextmanager
    def connect(self):
        c = sqlite3.connect(self.path, timeout=30)
        c.row_factory = sqlite3.Row
        try:
            c.execute("PRAGMA busy_timeout=30000")
            c.execute("PRAGMA journal_mode=WAL")
            with c:
                yield c
        finally:
            c.close()

    def kb(self, identity):
        with self.connect() as c:
            row = c.execute(
                "SELECT * FROM knowledge_bases WHERE id=?", (identity,)
            ).fetchone()
        if row is None:
            raise KeyError("Knowledge base not found")
        return dict(id=row["id"], revision=row["revision"], **json.loads(row["data"]))

    def list_kbs(self):
        with self.connect() as c:
            ids = [
                r[0]
                for r in c.execute(
                    "SELECT id FROM knowledge_bases ORDER BY json_extract(data,'$.created_at') DESC,id"
                )
            ]
        return [self.kb(i) for i in ids]

    def create_kb(self, value, *, identity=None):
        value = KnowledgeBaseCreate.model_validate(value).model_dump()
        identity = identity or uuid4().hex
        value["created_at"] = time.time()
        with self.connect() as c:
            c.execute(
                "INSERT INTO knowledge_bases(id,data) VALUES (?,?)",
                (identity, json.dumps(value)),
            )
        (self.root / "bases" / identity / "knowledge").mkdir(
            parents=True, exist_ok=True
        )
        return self.kb(identity)

    def configure(self, identity, value, expected_revision):
        old = self.kb(identity)
        value = KnowledgeBaseCreate.model_validate(value).model_dump()
        value["created_at"] = old["created_at"]
        with self.connect() as c:
            if (
                c.execute(
                    "UPDATE knowledge_bases SET data=?,revision=revision+1 WHERE id=? AND revision=?",
                    (json.dumps(value), identity, expected_revision),
                ).rowcount
                != 1
            ):
                raise ValueError("Configuration changed; refresh before saving")
        return self.kb(identity)

    def add_model(self, config, *, identity=None):
        config = ModelConfig.model_validate(config).model_dump()
        identity = (
            identity
            or "model-"
            + hashlib.sha256(json.dumps(config, sort_keys=True).encode()).hexdigest()[
                :24
            ]
        )
        with self.connect() as c:
            row = c.execute(
                "SELECT config FROM models WHERE id=?", (identity,)
            ).fetchone()
            if row and json.loads(row[0]) != config:
                raise ValueError("Model IDs are immutable; create a new model version")
            c.execute(
                "INSERT OR IGNORE INTO models(id,config) VALUES (?,?)",
                (identity, json.dumps(config)),
            )
        return identity

    def model(self, identity, *, require_enabled=False):
        with self.connect() as c:
            row = c.execute("SELECT * FROM models WHERE id=?", (identity,)).fetchone()
        if row is None:
            raise KeyError("Model not found")
        if require_enabled and not row["enabled"]:
            raise ValueError("Model is disabled for new configuration/builds")
        return dict(
            id=row["id"], enabled=bool(row["enabled"]), config=json.loads(row["config"])
        )

    def models(self):
        with self.connect() as c:
            ids = [r[0] for r in c.execute("SELECT id FROM models ORDER BY id")]
        return [self.model(i) for i in ids]

    def enable_model(self, identity, enabled):
        self.model(identity)
        with self.connect() as c:
            c.execute(
                "UPDATE models SET enabled=? WHERE id=?", (int(enabled), identity)
            )

    def create_key(self, value):
        for kb in value.knowledge_base_ids:
            self.kb(kb)
        identity = uuid4().hex
        token = "rag_" + identity + "." + secrets.token_urlsafe(32)
        with self.connect() as c:
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

    def enqueue(self, kb_id, operation, payload, idempotency=None):
        self.kb(kb_id)
        identity = uuid4().hex
        now = time.time()
        encoded = json.dumps(payload, sort_keys=True)
        with self.connect() as c:
            c.execute("BEGIN IMMEDIATE")
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

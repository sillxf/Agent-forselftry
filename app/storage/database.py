"""Shared connection/schema; domain repositories own their SQL."""

from contextlib import contextmanager
from pathlib import Path
import sqlite3

SCHEMA = "\nCREATE TABLE IF NOT EXISTS knowledge_bases(id TEXT PRIMARY KEY, data TEXT NOT NULL, revision INTEGER NOT NULL DEFAULT 1);\nCREATE TABLE IF NOT EXISTS models(id TEXT PRIMARY KEY, config TEXT NOT NULL, enabled INTEGER NOT NULL DEFAULT 1);\nCREATE TABLE IF NOT EXISTS api_keys(id TEXT PRIMARY KEY, name TEXT NOT NULL, digest TEXT NOT NULL, scopes TEXT NOT NULL, rpm INTEGER NOT NULL, revoked INTEGER NOT NULL DEFAULT 0);\nCREATE TABLE IF NOT EXISTS quota(key_id TEXT NOT NULL, minute INTEGER NOT NULL, used INTEGER NOT NULL, PRIMARY KEY(key_id,minute));\nCREATE TABLE IF NOT EXISTS jobs(id TEXT PRIMARY KEY,kb_id TEXT NOT NULL,operation TEXT NOT NULL,payload TEXT NOT NULL,status TEXT NOT NULL,stage TEXT NOT NULL,created REAL NOT NULL,updated REAL NOT NULL,error TEXT,result TEXT,idempotency TEXT UNIQUE);\nCREATE TABLE IF NOT EXISTS audit(id INTEGER PRIMARY KEY,at REAL NOT NULL,actor TEXT NOT NULL,action TEXT NOT NULL,kb_id TEXT,details TEXT NOT NULL);\n"


class Database:
    def __init__(self, root):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "catalog.sqlite3"
        with self.connect() as connection:
            version = connection.execute("PRAGMA user_version").fetchone()[0]
            if version not in {0, 1}:
                raise ValueError(
                    "Unsupported catalog schema; restore matching code/data"
                )
            connection.executescript(SCHEMA)
            connection.execute("PRAGMA user_version=1")

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

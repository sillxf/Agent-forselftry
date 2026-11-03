"""Knowledge-base records only."""

import json, time
from uuid import uuid4
from app.core.contracts import KnowledgeBaseCreate


class KnowledgeBaseRepository:
    def __init__(self, database):
        self.root, self.connect = database.root, database.connect

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

"""Immutable model definitions and enablement."""

import hashlib, json
from app.core.contracts import ModelConfig


class ModelRepository:
    def __init__(self, connect):
        self.connect = connect

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

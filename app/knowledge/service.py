"""Knowledge-base configuration and publication inspection commands."""

from uuid import uuid4
from app.core.serialization import public


class KnowledgeService:
    def __init__(self, bases, models, workspaces, jobs, access, audit):
        (
            self.repository,
            self.models,
            self.workspaces,
            self.jobs,
            self.access,
            self.audit,
        ) = bases, models, workspaces, jobs, access, audit

    def create(self, actor, configuration):
        self.access.authorize(actor, admin=True)
        self.validate_config(configuration)
        identity = uuid4().hex
        with self.workspaces.maintenance_lock(identity):
            result = self.repository.create_kb(
                configuration.model_dump(), identity=identity
            )
            self.audit.audit(actor["id"], "knowledge_base_created", result["id"])
            return result

    def configure(self, actor, kb_id, configuration, revision):
        with self.workspaces.maintenance_lock(kb_id):
            self.access.authorize(actor, kb_id, admin=True)
            self.validate_config(configuration)
            result = self.repository.configure(
                kb_id, configuration.model_dump(), revision
            )
            self.audit.audit(
                actor["id"], "configuration_changed", kb_id, revision=result["revision"]
            )
            return result

    def delete(self, actor, kb_id):
        from filelock import FileLock
        from app.knowledge.purge import remove_managed

        self.access.authorize(actor, admin=True)
        with self.workspaces.maintenance_lock(kb_id):
            bases = self.repository.root / "bases"
            base = bases / kb_id
            if base.is_symlink() or not base.resolve().is_relative_to(
                self.repository.root.resolve()
            ):
                raise ValueError("Refusing deletion outside the managed data root")
            try:
                self.repository.kb(kb_id, include_deleting=True)
            except KeyError:
                if base.exists():
                    raise
                return {"id": kb_id, "status": "completed"}
            # Legacy build/source locks are a preflight check. The outer gate keeps
            # all current API/Worker writers out while the directory is removed.
            storage = base / "storage"
            if storage.exists():
                with (
                    FileLock(str(storage / "build.lock"), timeout=0),
                    FileLock(str(storage / "sources.lock"), timeout=0),
                ):
                    pass
            self.repository.begin_delete(
                kb_id
            )  # Durable, fail-closed on any partial removal.
            remove_managed(base, bases)
            self.jobs.delete_for_base(kb_id)
            self.access.keys.remove_scope(kb_id)
            self.repository.finish_delete(kb_id)
            self.workspaces.discard(kb_id)
            self.audit.audit(actor["id"], "knowledge_base_deleted", kb_id)
            return {"id": kb_id, "status": "completed"}

    def generations(self, actor, kb_id):
        self.access.authorize(actor, kb_id, admin=True)
        runtime = self.workspaces.get(kb_id)
        return public(
            dict(
                current=runtime.repository.current_pointer(),
                publications=runtime.repository.publications(),
            )
        )

    def validate_config(self, body):
        embedding = self.models.model(body.build.embedding_id, require_enabled=True)
        reranker = self.models.model(body.profile.reranker_id, require_enabled=True)
        if (
            embedding["config"]["kind"] != "embedding"
            or reranker["config"]["kind"] != "reranker"
        ):
            raise ValueError("Incorrect model role")

    def status(self, actor, kb_id):
        kb = self.access.authorize(actor, kb_id)
        r = self.workspaces.get(kb_id)
        pointer = r.repository.current_pointer()
        manifest = (
            r.repository._read_manifest(pointer["generation"]) if pointer else None
        )
        active = pointer["signature"]["model"] if pointer else None
        desired = "provider:" + kb["build"]["embedding_id"]
        # Compare the entire desired build identity, not merely model names.
        sig = pointer.get("signature", {}) if pointer else {}
        build = kb["build"]
        needs_build = (
            not pointer
            or active != desired
            or any(
                sig.get(k) != build[v]
                for k, v in [
                    ("parent_tokens", "parent_tokens"),
                    ("child_tokens", "child_tokens"),
                    ("overlap", "overlap_tokens"),
                    ("ocr", "ocr_enabled"),
                ]
            )
        )
        return public(
            dict(
                knowledge_base=kb,
                current=pointer,
                counts=manifest["counts"] if manifest else {},
                active_embedding=active,
                desired_embedding=desired,
                configuration_pending=needs_build,
                core_jobs=r.registry.list_jobs(),
                jobs=self.jobs.jobs(kb_id),
            )
        )

    def list(self, actor):
        return [
            item
            for item in self.repository.list_kbs()
            if actor["admin"] or item["id"] in actor["scopes"]
        ]

    def ready(self, actor):
        bases = self.list(actor)
        return {
            "status": "ready",
            "knowledge_bases": len(bases),
            "published": sum(
                bool(self.workspaces.get(k["id"]).repository.current_pointer())
                for k in bases
                if not k.get("deleting")
            ),
        }

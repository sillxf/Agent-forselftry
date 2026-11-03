"""Read-only inspection of published documents, chunks and outlines."""

from pathlib import Path
import json
from app.core.serialization import public


class DocumentInspectionService:
    def __init__(self, workspaces, access):
        self.workspaces, self.access = workspaces, access

    def documents(self, actor, kb_id):
        self.access.authorize(actor, kb_id)
        r = self.workspaces.get(kb_id)
        pointer = r.repository.current_pointer()
        manifest = r.repository._read_manifest(pointer["generation"]) if pointer else {}
        published = {x["document_id"]: x for x in (manifest or {}).get("documents", [])}
        output = []
        for d in r.registry.list_documents():
            state = (
                "purged"
                if d.purged_at
                else "deleted"
                if d.deleted_at
                else "published"
                if d.document_id in published
                else "uploaded"
            )
            purge_state = None
            if d.purged_at:
                path = r.storage_dir / "purges" / (d.document_id + ".json")
                purge_state = (
                    json.loads(path.read_text())["status"]
                    if path.exists()
                    else "plan_unavailable"
                )
                if purge_state == "completed":
                    continue  # Keep the internal tombstone, not a deleted row in the UI.
                state = "purge_incomplete"
            versions = r.registry.list_versions(d.document_id)
            served = published.get(d.document_id)
            output.append(
                public(
                    dict(
                        **d.model_dump(),
                        name=Path(d.source_path).name,
                        file_type=versions[-1].file_type if versions else "",
                        status=state,
                        purge_state=purge_state,
                        published=served,
                        needs_build=not d.purged_at
                        and not d.deleted_at
                        and (
                            not served
                            or served.get("version_id")
                            != (d.selected_version_id or d.latest_version_id)
                        ),
                        versions=[v.model_dump() for v in versions],
                        view_states=r.registry.view_states(d.document_id),
                        view_count=sum(
                            v["count"]
                            for v in (manifest or {}).get("view_assets", [])
                            if v["document_id"] == d.document_id
                        ),
                    )
                )
            )
        return output

    def document(
        self, actor, kb_id, document_id, *, generation_id=None, offset=0, limit=50
    ):
        self.access.authorize(actor, kb_id)
        r = self.workspaces.get(kb_id)
        d = r.registry.get_document(document_id)
        if d.purged_at or d.deleted_at:
            raise KeyError("Document unavailable")
        pointer = r.repository.current_pointer()
        if generation_id and generation_id not in {
            p["generation"] for p in r.repository.publications() if p["available"]
        }:
            raise KeyError("Generation was never published or is unavailable")
        snapshot = (
            r.repository.load_generation(generation_id)
            if generation_id
            else r.repository.load_generation(pointer["generation"])
            if pointer
            else None
        )
        record = (
            next((x for x in snapshot.documents if x.document_id == document_id), None)
            if snapshot
            else None
        )
        parents = (
            [
                p.model_dump(mode="json")
                for p in snapshot.parents
                if p.document_id == document_id
            ]
            if snapshot
            else []
        )
        children = (
            [c for c in snapshot.store.records if c["document_id"] == document_id]
            if snapshot
            else []
        )
        ids = {c["chunk_id"] for c in children}
        views = (
            [v for v in snapshot.view_store.records if v["source_child_id"] in ids]
            if snapshot and snapshot.view_store
            else []
        )
        markdown = None
        if record:
            path = r.storage_dir / "parsed" / (record.checksum + ".md")
            if path.exists():
                markdown = path.read_text(encoding="utf-8")
        return public(
            dict(
                document=d.model_dump(),
                generation_id=generation_id or (pointer or {}).get("generation"),
                published=record.model_dump(mode="json") if record else None,
                markdown=markdown[:200000] if markdown else markdown,
                markdown_truncated=bool(markdown and len(markdown) > 200000),
                pagination={
                    "offset": offset,
                    "limit": limit,
                    "parents": len(parents),
                    "children": len(children),
                    "views": len(views),
                },
                parents=parents[offset : offset + limit],
                children=children[offset : offset + limit],
                views=views[offset : offset + limit],
                outline=[
                    {
                        "section_path": p["section_path"],
                        "page_start": p["page_start"],
                        "parent_id": p["parent_id"],
                    }
                    for p in parents[:1000]
                ],
            )
        )

    def chunk(self, actor, kb_id, chunk_id, *, generation_id=None):
        self.access.authorize(actor, kb_id)
        r = self.workspaces.get(kb_id)
        pointer = r.repository.current_pointer()
        if not pointer and not generation_id:
            raise KeyError("No published index")
        if generation_id and generation_id not in {
            p["generation"] for p in r.repository.publications() if p["available"]
        }:
            raise KeyError("Generation was never published or is unavailable")
        snapshot = r.repository.load_generation(generation_id or pointer["generation"])
        item = next(
            (x for x in snapshot.store.records if x["chunk_id"] == chunk_id), None
        )
        if item is None or item["document_id"] not in r.registry.eligible_ids(
            [item["document_id"]]
        ):
            raise KeyError("Chunk unavailable")
        return public(item)

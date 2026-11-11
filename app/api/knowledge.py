"""General-purpose knowledge API. Administration is local-only unless token protected."""
import hmac
import ipaddress
import json
import logging
import os
from pathlib import Path
import sqlite3
from typing import Literal
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from filelock import Timeout
from pydantic import BaseModel, ConfigDict

from app.rag.ingestion.docling_parser import SUPPORTED_EXTENSIONS, file_checksum
from app.rag.retrieval.policy import RetrievalPolicy
from app.rag.view_generation import ViewConfig

logger = logging.getLogger(__name__)


class DocumentSettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    metadata: dict[str, str] | None = None
    view_config: ViewConfig | None = None


class ValiditySettings(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_at: str | None = None
    expires_at: str | None = None


class VersionSelection(BaseModel):
    version_id: UUID


class Confirmation(BaseModel):
    confirm: bool


def require_admin(request: Request):
    origin = request.headers.get("origin")
    if origin and origin.rstrip("/") != f"{request.url.scheme}://{request.url.netloc}":
        raise HTTPException(403, "Cross-origin administration is forbidden")
    token = os.getenv("RAG_ADMIN_TOKEN")
    if token:
        supplied = request.headers.get("authorization", "")
        if not hmac.compare_digest(supplied, "Bearer " + token):
            raise HTTPException(401, "A valid RAG_ADMIN_TOKEN is required")
    else:
        try:
            local = ipaddress.ip_address(request.client.host).is_loopback if request.client else False
        except ValueError:
            local = False
        if not local or request.url.hostname not in {"127.0.0.1", "localhost", "::1"}:
            raise HTTPException(403, "Administration requires loopback client/host; configure RAG_ADMIN_TOKEN for remote access")


def action(call):
    try:
        return call()
    except KeyError as exc:
        raise HTTPException(404, "Document/version not found") from exc
    except Timeout as exc:
        raise HTTPException(409, "Another build or maintenance operation is active") from exc
    except ValueError as exc:
        raise HTTPException(409, str(exc)) from exc
    except (OSError, sqlite3.DatabaseError, RuntimeError) as exc:
        logger.exception("Knowledge operation failed")
        raise HTTPException(503, "Knowledge operation failed; inspect jobs and storage integrity") from exc


def create_knowledge_router(retriever, *, search_provider=None):
    router = APIRouter(prefix="/knowledge", tags=["knowledge"])
    admin = [Depends(require_admin)]

    @router.get("/search")
    def search(request: Request, q: str = Query(..., min_length=1, max_length=4000), k: int = Query(3, ge=1, le=20),
               include_trace: bool = False, supplement: bool = False, as_of: str | None = None,
               retrieval_mode: Literal["hybrid", "multi_view"] = "hybrid"):
        # Legacy HTTP multi_view now means the same governed, explicit supplement request.
        if as_of is not None:
            require_admin(request)
        active = search_provider() if search_provider else retriever
        action(active.refresh_policy)
        if retrieval_mode == "multi_view" and (not active.orchestrator.policy.multi_view_enabled or active.pipeline.multi_view_dense is None):
            raise HTTPException(409, "Multi-View is disabled or unavailable; use a trace-enabled supplement request for fallback")
        output = action(lambda: active.search_with_trace(q, k, supplement=supplement or retrieval_mode == "multi_view", as_of=as_of))
        return {"query":q, **(output if include_trace else {"results":output["results"]})}

    @router.get("/admin")
    def page():
        return FileResponse(Path(__file__).resolve().parents[1] / "static/knowledge/index.html",
            headers={"Content-Security-Policy":"default-src 'self'; script-src 'self'; style-src 'self'; frame-ancestors 'none'",
                     "Cache-Control":"no-store"})

    @router.get("/status", dependencies=admin)
    def status():
        def read():
            pointer = retriever.repository.current_pointer()
            manifest = retriever.repository._read_manifest(pointer["generation"]) if pointer else None
            return {"current":pointer, "manifest":manifest, "last_build_error":retriever.last_build_error,
                    "last_refresh_error":retriever.last_refresh_error,
                    "documents":len(retriever.registry.list_documents()),
                    "view_states":retriever.registry.view_states(), "jobs":retriever.registry.list_jobs()}
        return action(read)

    @router.get("/documents", dependencies=admin)
    def documents():
        def read():
            output = []
            pointer = retriever.repository.current_pointer()
            manifest = retriever.repository._read_manifest(pointer["generation"]) if pointer else None
            served = {r["document_id"]:r for r in manifest["documents"]} if manifest else {}
            counts = {}
            if pointer:
                with sqlite3.connect(retriever.repository.root / pointer["generation"] / "metadata.db") as connection:
                    for table in ("parents", "chunks"):
                        for identity, count in connection.execute(f"SELECT document_id, COUNT(*) FROM {table} GROUP BY document_id"):
                            counts.setdefault(identity, {})[table] = count
            for document in retriever.registry.list_documents():
                data = document.model_dump()
                data["published"] = served.get(document.document_id)
                data["view_states"] = retriever.registry.view_states(document.document_id)
                data["published_view_count"] = sum(v["count"] for v in (manifest or {}).get("view_assets", []) if v["document_id"] == document.document_id)
                data["purge_state"] = None
                if document.purged_at:
                    try:
                        plan = json.loads((retriever.storage_dir / "purges" / (document.document_id + ".json")).read_text(encoding="utf-8"))
                        data["purge_state"] = plan["status"]
                    except (OSError, ValueError, KeyError):
                        data["purge_state"] = "plan_unavailable"
                data["versions"] = [v.model_dump() for v in retriever.registry.list_versions(document.document_id)]
                data["needs_build"] = (not document.purged_at and
                    (data["published"] or {}).get("version_id") != (document.selected_version_id or document.latest_version_id))
                data["counts"] = counts.get(document.document_id, {})
                data["processing_status"] = ("purged" if data["purge_state"] == "completed" else "purge_incomplete") if document.purged_at else "deleted" if document.deleted_at else "pending" if data["needs_build"] else "published"
                output.append(data)
            return output
        return action(read)

    @router.post("/documents", dependencies=admin, status_code=201)
    async def upload(request: Request, filename: str = Query(..., min_length=1, max_length=180), document_id: UUID | None = None):
        # Raw streamed upload: no multipart parser, external URL fetching or arbitrary paths.
        if Path(filename).name != filename or any(c in filename for c in '/\\:\x00') or any(ord(c) < 32 for c in filename):
            raise HTTPException(422, "Upload requires a plain filename")
        if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise HTTPException(422, "Unsupported document format")
        limit = int(os.getenv("RAG_UPLOAD_MAX_BYTES", str(25 * 1024 * 1024)))
        uploads = retriever.knowledge_dir / "uploads"
        uploads.mkdir(parents=True, exist_ok=True)
        temporary = uploads / ("." + uuid4().hex + ".upload")
        total = 0
        try:
            with temporary.open("xb") as stream:
                async for chunk in request.stream():
                    total += len(chunk)
                    if total > limit:
                        raise HTTPException(413, "Document exceeds upload size limit")
                    stream.write(chunk)
            if not total:
                raise HTTPException(422, "Empty document upload")
            def capture():
                with retriever.build_service.lock:
                    if document_id:
                        existing = retriever.registry.get_document(str(document_id))
                        if existing.deleted_at or existing.purged_at:
                            raise ValueError("Restore a soft-deleted document before updating; purged documents cannot be updated")
                        target = Path(existing.source_path)
                        if target.suffix.lower() != Path(filename).suffix.lower():
                            raise ValueError("An update must keep the document file type")
                    else:
                        target = uploads / uuid4().hex / filename
                    if target.is_symlink() or not target.resolve().is_relative_to(retriever.knowledge_dir.resolve()):
                        raise ValueError("Uploads may only update documents inside the managed knowledge directory")
                    target.parent.mkdir(parents=True, exist_ok=True)
                    previous = target.read_bytes() if target.exists() else None
                    try:
                        temporary.replace(target)
                        document, version = retriever.lifecycle.import_document(target)
                    except Exception:
                        if previous is None:
                            target.unlink(missing_ok=True)
                        else:
                            target.write_bytes(previous)
                        raise
                    return {"document":document.model_dump(), "version":version.model_dump(), "needs_build":True}
            return action(capture)
        finally:
            temporary.unlink(missing_ok=True)

    @router.patch("/documents/{document_id}", dependencies=admin)
    def configure(document_id: UUID, settings: DocumentSettings):
        if settings.metadata is not None and (len(settings.metadata) > 30 or any(len(k)>100 or len(v)>2000 for k,v in settings.metadata.items())):
            raise HTTPException(422, "Metadata exceeds limits")
        return action(lambda: retriever.registry.configure(str(document_id), metadata=settings.metadata,
            view_config=settings.view_config.model_dump() if settings.view_config else None).model_dump())

    @router.put("/documents/{document_id}/validity", dependencies=admin)
    def validity(document_id: UUID, settings: ValiditySettings):
        return action(lambda: retriever.lifecycle.set_validity(str(document_id), **settings.model_dump()).model_dump())

    @router.delete("/documents/{document_id}", dependencies=admin)
    def delete(document_id: UUID):
        return action(lambda: retriever.lifecycle.delete(str(document_id)).model_dump())

    @router.post("/documents/{document_id}/restore", dependencies=admin)
    def restore(document_id: UUID):
        return action(lambda: retriever.lifecycle.restore(str(document_id)).model_dump())

    @router.post("/documents/{document_id}/restore-version", dependencies=admin)
    def restore_content(document_id: UUID, selection: VersionSelection):
        return action(lambda: retriever.restore_version(str(document_id), str(selection.version_id)).model_dump())

    @router.delete("/documents/{document_id}/purge", dependencies=admin)
    def purge(document_id: UUID, confirmation: Confirmation):
        if not confirmation.confirm:
            raise HTTPException(422, "Hard deletion requires explicit confirmation")
        return action(lambda: retriever.purge_document(str(document_id)))

    @router.get("/documents/{document_id}/source", dependencies=admin)
    def download(document_id: UUID, version_id: UUID | None = None):
        def read():
            document = retriever.registry.get_document(str(document_id))
            if document.purged_at:
                raise KeyError(str(document_id))
            selected = str(version_id) if version_id else document.selected_version_id or document.latest_version_id
            version = next((v for v in retriever.registry.list_versions(str(document_id)) if v.version_id == selected), None)
            if version is None:
                raise KeyError(selected)
            path = Path(version.source_blob_path)
            if not path.resolve().is_relative_to((retriever.storage_dir / "sources").resolve()) or file_checksum(path) != version.content_hash:
                raise ValueError("Source blob is outside managed storage or corrupt")
            return FileResponse(path, filename=Path(document.source_path).name, media_type="application/octet-stream",
                headers={"X-Content-Type-Options":"nosniff", "Cache-Control":"no-store"})
        return action(read)

    @router.get("/policy", dependencies=admin)
    def policy():
        retriever.refresh_policy()
        return retriever.orchestrator.policy.model_dump()

    @router.put("/policy", dependencies=admin)
    def configure_policy(settings: RetrievalPolicy):
        return action(lambda: retriever.set_policy(settings).model_dump())

    @router.get("/generations", dependencies=admin)
    def generations():
        def read():
            pointer = retriever.repository.current_pointer()
            published = retriever.repository.publications()
            output = []
            for path in sorted(retriever.repository.root.glob("*/manifest.json"), key=lambda p:p.stat().st_mtime, reverse=True):
                try:
                    item = retriever.repository._read_manifest(path.parent.name)
                    output.append({"generation_id":path.parent.name, "current":bool(pointer and pointer["generation"] == path.parent.name),
                        "created_at":item["created_at"], "counts":item["counts"], "documents":item["documents"], "healthy":True})
                except (ValueError, OSError):
                    output.append({"generation_id":path.parent.name, "healthy":False})
            return {"generations":output, "publications":published}
        return action(read)

    @router.post("/build", dependencies=admin, status_code=202)
    def build(full: bool = False):
        running = retriever._build_future is not None and not retriever._build_future.done()
        if not running and not action(retriever.build_service.recover):
            raise HTTPException(409, "Another build or maintenance operation is active")
        future = action(lambda: retriever.build_index_async(full=full))
        return {"accepted":True, "finished":future.done()}

    @router.post("/rollback/{generation}", dependencies=admin)
    def rollback(generation: str):
        return {"job_id":action(lambda: retriever.rollback_generation(generation))}

    @router.post("/gc", dependencies=admin)
    def gc(keep: int = Query(3, ge=2), min_age_seconds: int = Query(86400, ge=0)):
        from app.rag.indexing.maintenance import collect_generations
        return action(lambda: collect_generations(retriever.build_service, keep=keep, min_age_seconds=min_age_seconds))

    return router

"""Versioned HTTP adapter. All identities and content access pass through RAGService."""

from contextlib import asynccontextmanager
from pathlib import Path
from uuid import UUID, uuid4
import json, os, tempfile
import httpx
import sqlite3
from urllib.parse import urlsplit
from fastapi import FastAPI, Request, HTTPException, Depends, Query
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field
from filelock import Timeout, FileLock
from rag_service.contracts import (
    KnowledgeBaseCreate,
    SearchRequest,
    SearchResponse,
    ModelConfig,
    KeyCreate,
    JobRequest,
)
from rag_service.service import RAGService, AccessDenied, BusyError, public
from rag_service.core.view_generation import ViewConfig
from rag_service.core.ingestion.docling_parser import SUPPORTED_EXTENSIONS


class DocumentPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    metadata: dict[str, str] | None = None
    view_config: ViewConfig | None = None


class Validity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_at: str | None = None
    expires_at: str | None = None


class RestoreVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version_id: UUID


class Enabled(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool


def create_app(service=None, *, with_mcp=True):
    service = service or RAGService(
        os.getenv("RAG_SERVICE_DATA", str(Path.home() / ".rag-service"))
    )
    mcp = None
    if with_mcp:
        from rag_service.mcp import create_mcp

        mcp = create_mcp(service=service)
        mcp_app = mcp.streamable_http_app()

    @asynccontextmanager
    async def lifespan(app):
        with FileLock(str(service.root / "server.lock"), timeout=0):
            if mcp:
                async with mcp.session_manager.run():
                    yield
            else:
                yield

    app = FastAPI(
        title="RAG Knowledge Service",
        version="1.0.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.service = service
    allowed_hosts = set(
        os.getenv("RAG_ALLOWED_HOSTS", "localhost,127.0.0.1,::1").split(",")
    )
    allowed_origins = set(filter(None, os.getenv("RAG_ALLOWED_ORIGINS", "").split(",")))

    @app.middleware("http")
    async def boundary(request, call_next):
        if request.url.hostname not in allowed_hosts:
            return JSONResponse({"detail": "Host is not allowed"}, 403)
        origin = request.headers.get("origin")
        if origin and origin.rstrip("/") not in allowed_origins | {
            f"{request.url.scheme}://{request.url.netloc}"
        }:
            return JSONResponse({"detail": "Cross-origin request rejected"}, 403)
        if request.url.path.startswith(("/api/", "/mcp")):
            auth = request.headers.get("authorization", "")
            try:
                request.state.actor = service.authenticate(
                    auth.removeprefix("Bearer ") if auth.startswith("Bearer ") else ""
                )
            except AccessDenied:
                return JSONResponse(
                    {"detail": "Valid Bearer credentials required"},
                    401,
                    headers={"WWW-Authenticate": "Bearer"},
                )
        upload_path = request.method == "POST" and request.url.path.endswith(
            "/documents"
        )
        if (
            request.method in {"POST", "PUT", "PATCH"}
            and not upload_path
            and not request.url.path.startswith("/mcp")
        ):
            chunks = []
            size = 0
            async for block in request.stream():
                size += len(block)
                if size > 65536:
                    return JSONResponse({"detail": "Request exceeds 64 KiB"}, 413)
                chunks.append(block)
            request._body = b"".join(chunks)
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["Referrer-Policy"] = "no-referrer"
        response.headers["Cache-Control"] = "no-store"
        response.headers["Content-Security-Policy"] = (
            "default-src 'self'; script-src 'self'; style-src 'self' 'unsafe-inline'; frame-ancestors 'none'; object-src 'none'"
        )
        return response

    @app.exception_handler(AccessDenied)
    async def denied(request, exc):
        return JSONResponse({"detail": str(exc)}, 403)

    @app.exception_handler(PermissionError)
    async def limited(request, exc):
        return JSONResponse(
            {"detail": "Rate limit exceeded"}, 429, headers={"Retry-After": "60"}
        )

    @app.exception_handler(KeyError)
    async def missing(request, exc):
        return JSONResponse({"detail": "Requested resource is unavailable"}, 404)

    @app.exception_handler(ValueError)
    async def invalid(request, exc):
        return JSONResponse({"detail": str(exc)}, 409)

    @app.exception_handler(Timeout)
    async def locked(request, exc):
        return JSONResponse({"detail": "Knowledge maintenance is busy"}, 409)

    @app.exception_handler(BusyError)
    async def busy(request, exc):
        return JSONResponse({"detail": str(exc)}, 503)

    @app.exception_handler(OSError)
    async def storage(request, exc):
        return JSONResponse(
            {"detail": "Storage operation failed; inspect service log"}, 503
        )

    @app.exception_handler(httpx.HTTPError)
    async def provider_unavailable(request, exc):
        return JSONResponse({"detail": "Upstream model service unavailable"}, 503)

    @app.exception_handler(sqlite3.DatabaseError)
    async def database_unavailable(request, exc):
        return JSONResponse({"detail": "Metadata storage unavailable"}, 503)

    @app.exception_handler(RuntimeError)
    async def unavailable(request, exc):
        return JSONResponse(
            {"detail": "Knowledge operation unavailable; inspect service log"}, 503
        )

    def actor(request: Request):
        return request.state.actor

    def admin(who=Depends(actor)):
        service.authorize(who, admin=True)
        return who

    @app.get("/health/live")
    def live():
        return {"status": "ok", "service": "rag-knowledge-service", "version": "1.0.0"}

    @app.get("/api/v1/health/ready")
    def ready(who=Depends(actor)):
        bases = service.list_kbs(who)
        return {
            "status": "ready",
            "knowledge_bases": len(bases),
            "published": sum(
                bool(service.runtime(k["id"]).repository.current_pointer())
                for k in bases
            ),
        }

    @app.get("/api/v1/openapi.json")
    def openapi(who=Depends(admin)):
        return app.openapi()

    @app.get("/api/v1/me")
    def me(who=Depends(actor)):
        return who

    @app.get("/api/v1/knowledge-bases")
    def bases(who=Depends(actor)):
        return service.list_kbs(who)

    @app.post("/api/v1/knowledge-bases", status_code=201)
    def create_base(body: KnowledgeBaseCreate, who=Depends(admin)):
        service.validate_config(body)
        kb = service.catalog.create_kb(body.model_dump())
        service.catalog.audit(who["id"], "knowledge_base_created", kb["id"])
        return kb

    @app.put("/api/v1/knowledge-bases/{kb_id}")
    def configure(
        kb_id: UUID,
        body: KnowledgeBaseCreate,
        revision: int = Query(..., ge=1),
        who=Depends(admin),
    ):
        identity = kb_id.hex
        service.authorize(who, identity, admin=True)
        service.validate_config(body)
        result = service.catalog.configure(identity, body.model_dump(), revision)
        service.catalog.audit(
            who["id"], "configuration_changed", identity, revision=result["revision"]
        )
        return result

    # KB identity is canonical lowercase uuid.hex, so URL aliases never create different roots.
    @app.get("/api/v1/knowledge-bases/{kb_id}/status")
    def status(kb_id: UUID, who=Depends(admin)):
        return service.status(who, kb_id.hex)

    @app.post(
        "/api/v1/search",
        response_model=SearchResponse,
        response_model_exclude_unset=True,
    )
    def search(body: SearchRequest, who=Depends(actor)):
        return service.search(who, body)

    @app.get("/api/v1/knowledge-bases/{kb_id}/documents")
    def documents(kb_id: UUID, who=Depends(actor)):
        return service.documents(who, kb_id.hex)

    @app.get("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}")
    def document(
        kb_id: UUID,
        document_id: UUID,
        generation_id: str | None = None,
        offset: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        who=Depends(actor),
    ):
        return service.document(
            who,
            kb_id.hex,
            str(document_id),
            generation_id=generation_id,
            offset=offset,
            limit=limit,
        )

    @app.get("/api/v1/knowledge-bases/{kb_id}/chunks/{chunk_id}")
    def chunk(
        kb_id: UUID,
        chunk_id: UUID,
        generation_id: str | None = None,
        who=Depends(actor),
    ):
        return service.chunk(who, kb_id.hex, str(chunk_id), generation_id=generation_id)

    @app.post("/api/v1/knowledge-bases/{kb_id}/documents", status_code=201)
    async def upload(
        kb_id: UUID,
        request: Request,
        filename: str = Query(..., min_length=1, max_length=180),
        document_id: UUID | None = None,
        who=Depends(admin),
    ):
        identity = kb_id.hex
        service.authorize(who, identity, admin=True)
        r = service.runtime(identity)
        if (
            Path(filename).name != filename
            or any(c in filename for c in "/\\:\x00")
            or any(ord(c) < 32 for c in filename)
        ):
            raise ValueError("Use a plain filename")
        if Path(filename).suffix.lower() not in SUPPORTED_EXTENSIONS:
            raise ValueError("Unsupported document type")
        limit = int(os.getenv("RAG_UPLOAD_MAX_BYTES", str(25 * 1024 * 1024)))
        size = 0
        if document_id:
            d = r.registry.get_document(str(document_id))
            if d.purged_at or d.deleted_at:
                raise ValueError("Document is unavailable")
            target = Path(d.source_path)
            if not target.resolve().is_relative_to(r.knowledge_dir.resolve()):
                raise ValueError(
                    "External source is not an upload target; migrate it first"
                )
            if target.suffix.lower() != Path(filename).suffix.lower():
                raise ValueError("Document update must retain file type")
        else:
            target = r.knowledge_dir / uuid4().hex / filename
            target.parent.mkdir(parents=True, exist_ok=True)
        temporary = None
        try:
            with tempfile.NamedTemporaryFile(
                dir=r.knowledge_dir, suffix=".upload", delete=False
            ) as stream:
                temporary = Path(stream.name)
                async for block in request.stream():
                    size += len(block)
                    if size > limit:
                        raise HTTPException(413, "Document exceeds upload size limit")
                    stream.write(block)
            if size == 0:
                raise ValueError("Empty upload")
            with r.lifecycle.source_lock:
                # Keep writers/build source capture serialized; never replace an immutable source blob.
                temporary.replace(target)
                temporary = None
                record, version = r.lifecycle.import_document(target)
            service.catalog.audit(
                who["id"],
                "document_uploaded",
                identity,
                document_id=record.document_id,
                bytes=size,
            )
            return public(
                {
                    "document": record.model_dump(),
                    "version": version.model_dump(),
                    "needs_build": True,
                }
            )
        finally:
            if temporary is not None:
                temporary.unlink(missing_ok=True)

    @app.patch("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}")
    def patch_document(
        kb_id: UUID, document_id: UUID, body: DocumentPatch, who=Depends(admin)
    ):
        service.authorize(who, kb_id.hex, admin=True)
        if body.metadata and (
            len(body.metadata) > 50
            or any(len(k) > 100 or len(v) > 2000 for k, v in body.metadata.items())
        ):
            raise ValueError("Metadata exceeds limits")
        r = service.runtime(kb_id.hex)
        result = r.registry.configure(
            str(document_id),
            metadata=body.metadata,
            view_config=body.view_config.model_dump() if body.view_config else None,
        )
        service.catalog.audit(
            who["id"], "document_configured", kb_id.hex, document_id=str(document_id)
        )
        return public(result.model_dump())

    @app.put("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/validity")
    def validity(kb_id: UUID, document_id: UUID, body: Validity, who=Depends(admin)):
        service.authorize(who, kb_id.hex, admin=True)
        result = service.runtime(kb_id.hex).registry.set_validity(
            str(document_id), **body.model_dump()
        )
        service.catalog.audit(
            who["id"], "validity_changed", kb_id.hex, document_id=str(document_id)
        )
        return public(result.model_dump())

    @app.delete("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}")
    def delete(kb_id: UUID, document_id: UUID, who=Depends(admin)):
        service.authorize(who, kb_id.hex, admin=True)
        r = service.runtime(kb_id.hex)
        result = r.registry.set_deleted(str(document_id))
        service.catalog.audit(
            who["id"], "document_deleted", kb_id.hex, document_id=str(document_id)
        )
        return public(result.model_dump())

    @app.post("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/undelete")
    def undelete(kb_id: UUID, document_id: UUID, who=Depends(admin)):
        service.authorize(who, kb_id.hex, admin=True)
        result = service.runtime(kb_id.hex).registry.set_deleted(
            str(document_id), False
        )
        service.catalog.audit(
            who["id"], "document_restored", kb_id.hex, document_id=str(document_id)
        )
        return public(result.model_dump())

    @app.post("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/restore-version")
    def restore_version(
        kb_id: UUID, document_id: UUID, body: RestoreVersion, who=Depends(admin)
    ):
        service.authorize(who, kb_id.hex, admin=True)
        result = service.runtime(kb_id.hex).restore_version(
            str(document_id), str(body.version_id)
        )
        service.catalog.audit(
            who["id"], "version_selected", kb_id.hex, document_id=str(document_id)
        )
        return public(result.model_dump())

    @app.get(
        "/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/original/{version_id}"
    )
    def original(kb_id: UUID, document_id: UUID, version_id: UUID, who=Depends(actor)):
        service.authorize(who, kb_id.hex)
        r = service.runtime(kb_id.hex)
        doc = r.registry.get_document(str(document_id))
        if doc.purged_at or doc.deleted_at:
            raise KeyError("Document unavailable")
        version = next(
            (
                v
                for v in r.registry.list_versions(str(document_id))
                if v.version_id == str(version_id)
            ),
            None,
        )
        if version is None:
            raise KeyError("Version not found")
        path = Path(version.source_blob_path)
        if not path.resolve().is_relative_to((r.storage_dir / "sources").resolve()):
            raise ValueError("Source is outside the managed root")
        service.catalog.audit(
            who["id"],
            "original_downloaded",
            kb_id.hex,
            document_id=str(document_id),
            version_id=str(version_id),
        )
        # Active HTML/office content is attachment-only, not rendered in the service origin.
        return FileResponse(
            path,
            filename=Path(doc.source_path).name,
            media_type="application/octet-stream",
        )

    @app.get("/api/v1/models")
    def models(who=Depends(admin)):
        return service.catalog.models()

    @app.post("/api/v1/models", status_code=201)
    def model(body: ModelConfig, who=Depends(admin)):
        identity = service.catalog.add_model(body.model_dump())
        service.catalog.audit(who["id"], "model_added", model_id=identity)
        return service.catalog.model(identity)

    @app.put("/api/v1/models/{model_id}/enabled")
    def enabled(model_id: str, body: Enabled, who=Depends(admin)):
        service.catalog.enable_model(model_id, body.enabled)
        service.catalog.audit(
            who["id"], "model_enabled", model_id=model_id, enabled=body.enabled
        )
        return service.catalog.model(model_id)

    @app.post("/api/v1/models/{model_id}/probe")
    def probe(model_id: str, confirm: bool = False, who=Depends(admin)):
        config = service.catalog.model(model_id, require_enabled=True)["config"]
        if not confirm:
            raise ValueError(
                "Explicit confirm=true is required; probing may load a model or incur provider charges"
            )
        from rag_service.providers import usage_context

        usage = []
        token = usage_context.set(usage)
        try:
            if config["kind"] == "embedding":
                vectors = service.providers.embedding(
                    "provider:" + model_id
                ).embed_query(["Connection probe"])
                result = {"dimension": int(vectors.shape[1])}
            else:
                rows = service.providers.reranker("provider:" + model_id).rerank(
                    "probe", [{"content": "probe"}]
                )
                result = {"score": rows[0]["reranker_score"]}
            service.catalog.audit(
                who["id"], "model_probed", model_id=model_id, usage=usage
            )
            return dict(**result, model_usage=usage)
        finally:
            usage_context.reset(token)

    @app.get("/api/v1/keys")
    def keys(who=Depends(admin)):
        return service.catalog.keys()

    @app.post("/api/v1/keys", status_code=201)
    def create_key(body: KeyCreate, who=Depends(admin)):
        result = service.catalog.create_key(body)
        service.catalog.audit(who["id"], "key_created", key_id=result["id"])
        return result

    @app.delete("/api/v1/keys/{key_id}")
    def revoke(key_id: str, who=Depends(admin)):
        service.catalog.revoke(key_id)
        service.catalog.audit(who["id"], "key_revoked", key_id=key_id)
        return {"revoked": True}

    @app.post("/api/v1/knowledge-bases/{kb_id}/jobs", status_code=202)
    def submit(kb_id: UUID, body: JobRequest, request: Request, who=Depends(admin)):
        idem = request.headers.get("idempotency-key")
        if idem and (len(idem) > 160 or len(idem) < 8):
            raise ValueError("Idempotency-Key must contain 8-160 characters")
        return service.submit(who, kb_id.hex, body, idempotency=idem)

    @app.get("/api/v1/jobs")
    def jobs(who=Depends(admin)):
        return public(service.catalog.jobs())

    @app.post("/api/v1/jobs/{job_id}/retry", status_code=202)
    def retry(job_id: UUID, who=Depends(admin)):
        old = service.catalog.job(job_id.hex)
        if old["status"] not in {"failed", "interrupted"}:
            raise ValueError("Only failed/interrupted jobs may be retried")
        payload = json.loads(old["payload"])
        request = JobRequest.model_validate(
            {k: v for k, v in payload.items() if k != "configuration"}
        )
        return service.submit(who, old["kb_id"], request)

    @app.get("/api/v1/knowledge-bases/{kb_id}/generations")
    def generations(kb_id: UUID, who=Depends(admin)):
        service.authorize(who, kb_id.hex, admin=True)
        r = service.runtime(kb_id.hex)
        return public(
            dict(
                current=r.repository.current_pointer(),
                publications=r.repository.publications(),
            )
        )

    @app.get("/api/v1/audit")
    def audits(who=Depends(admin)):
        return service.catalog.audits()

    if mcp:
        app.mount("/mcp", mcp_app)
    web = Path(__file__).parent / "web"
    if web.exists():
        app.mount("/", StaticFiles(directory=web, html=True), name="console")
    return app

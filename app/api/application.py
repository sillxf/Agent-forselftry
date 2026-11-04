"""Versioned HTTP adapter. Routes delegate to explicit domain services."""

from contextlib import asynccontextmanager
from pathlib import Path
import os
import httpx
import sqlite3
from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from filelock import Timeout, FileLock
from app.bootstrap import create_services
from app.api.dependencies import actor, admin
from app.api.console_session import ConsoleSession
from app.core.exceptions import AccessDenied, BusyError


def create_app(service=None, *, with_mcp=True, local_console=False):
    service = service or create_services(
        os.getenv("RAG_SERVICE_DATA", str(Path.cwd() / "storage"))
    )
    mcp = None
    if with_mcp:
        from mcp_server.server import create_mcp

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
        version="1.1.0",
        lifespan=lifespan,
        docs_url=None,
        redoc_url=None,
        openapi_url=None,
    )
    app.state.services = service
    console = ConsoleSession(enabled=local_console)
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
        if request.url.path == "/api/v1/console/session":
            return console.handle(request)
        if request.url.path.startswith(("/api/", "/mcp")):
            auth = request.headers.get("authorization", "")
            try:
                if (
                    not auth
                    and request.url.path.startswith("/api/")
                    and console.authenticate(request)
                ):
                    request.state.actor = {
                        "id": "local-console",
                        "admin": True,
                        "scopes": None,
                    }
                else:
                    request.state.actor = service.access.authenticate(
                        auth.removeprefix("Bearer ")
                        if auth.startswith("Bearer ")
                        else ""
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

    from app.api.routes import (
        health,
        knowledge,
        retrieval,
        documents,
        models,
        jobs,
        access,
    )

    for routes in (health, knowledge, retrieval, documents, models, jobs, access):
        app.include_router(routes.create_router(service, actor, admin, app))

    # KB identity is canonical lowercase uuid.hex, so URL aliases never create different roots.

    if mcp:
        app.mount("/mcp", mcp_app)
    web = Path(__file__).resolve().parents[1] / "web"
    if web.exists():
        app.mount("/", StaticFiles(directory=web, html=True), name="console")
    return app

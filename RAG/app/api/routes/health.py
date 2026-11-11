from fastapi import APIRouter, Depends
from app import __version__


def create_router(service, actor, admin, application):
    app = APIRouter()

    @app.get("/health/live")
    def live():
        return {"status": "ok", "service": "rag-knowledge-service", "version": __version__}

    @app.get("/api/v1/health/ready")
    def ready(who=Depends(actor)):
        return service.knowledge.ready(who)

    @app.get("/api/v1/openapi.json")
    def openapi(who=Depends(admin)):
        return application.openapi()

    @app.get("/api/v1/me")
    def me(who=Depends(actor)):
        return who

    return app

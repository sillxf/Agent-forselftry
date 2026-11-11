from fastapi import APIRouter, Depends
from app.core.contracts import ModelConfig
from app.api.schemas.knowledge import Enabled


def create_router(service, actor, admin, application):
    app = APIRouter()

    @app.get("/api/v1/models")
    def models(who=Depends(admin)):
        return service.models.list(who)

    @app.post("/api/v1/models", status_code=201)
    def model(body: ModelConfig, who=Depends(admin)):
        return service.models.add(who, body)

    @app.put("/api/v1/models/{model_id}/enabled")
    def enabled(model_id: str, body: Enabled, who=Depends(admin)):
        return service.models.enable(who, model_id, body.enabled)

    @app.post("/api/v1/models/{model_id}/probe")
    def probe(model_id: str, confirm: bool = False, who=Depends(admin)):
        return service.models.probe(who, model_id, confirm=confirm)

    return app

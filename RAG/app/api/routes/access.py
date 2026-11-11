from fastapi import APIRouter, Depends
from app.core.contracts import KeyCreate


def create_router(service, actor, admin, application):
    app = APIRouter()

    @app.get("/api/v1/keys")
    def keys(who=Depends(admin)):
        return service.access.list(who)

    @app.post("/api/v1/keys", status_code=201)
    def create_key(body: KeyCreate, who=Depends(admin)):
        return service.access.create(who, body)

    @app.delete("/api/v1/keys/{key_id}")
    def revoke(key_id: str, who=Depends(admin)):
        return service.access.revoke(who, key_id)

    @app.get("/api/v1/audit")
    def audits(who=Depends(admin)):
        service.access.authorize(who, admin=True)
        return service.audit.audits()

    return app

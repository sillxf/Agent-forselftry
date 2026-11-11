from uuid import UUID
from fastapi import APIRouter, Depends, Query
from app.core.contracts import KnowledgeBaseCreate


def create_router(service, actor, admin, application):
    app = APIRouter()

    @app.get("/api/v1/knowledge-bases")
    def bases(who=Depends(actor)):
        return service.knowledge.list(who)

    @app.post("/api/v1/knowledge-bases", status_code=201)
    def create_base(body: KnowledgeBaseCreate, who=Depends(admin)):
        return service.knowledge.create(who, body)

    @app.delete("/api/v1/knowledge-bases/{kb_id}")
    def delete_base(kb_id: UUID, confirm: bool = Query(False), who=Depends(admin)):
        if not confirm:
            raise ValueError("Permanent knowledge base deletion requires confirm=true")
        result = service.knowledge.delete(who, kb_id.hex)
        service.retrieval.sessions.discard(kb_id.hex)
        return result

    @app.put("/api/v1/knowledge-bases/{kb_id}")
    def configure(
        kb_id: UUID,
        body: KnowledgeBaseCreate,
        revision: int = Query(..., ge=1),
        who=Depends(admin),
    ):
        result = service.knowledge.configure(who, kb_id.hex, body, revision)
        # Drop sessions built for the previous profile; the next search loads anew.
        service.retrieval.sessions.discard(kb_id.hex)
        return result

    @app.get("/api/v1/knowledge-bases/{kb_id}/status")
    def status(kb_id: UUID, who=Depends(admin)):
        return service.knowledge.status(who, kb_id.hex)

    @app.get("/api/v1/knowledge-bases/{kb_id}/generations")
    def generations(kb_id: UUID, who=Depends(admin)):
        return service.knowledge.generations(who, kb_id.hex)

    return app

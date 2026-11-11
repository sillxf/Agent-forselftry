from uuid import UUID
from fastapi import APIRouter, Depends, Request
from app.core.contracts import JobControlRequest, JobRequest
from app.core.exceptions import InvalidRequest


def create_router(service, actor, admin, application):
    app = APIRouter()

    @app.post("/api/v1/knowledge-bases/{kb_id}/jobs", status_code=202)
    def submit(kb_id: UUID, body: JobRequest, request: Request, who=Depends(admin)):
        idem = request.headers.get("idempotency-key")
        if idem and (len(idem) > 160 or len(idem) < 8):
            raise InvalidRequest("Idempotency-Key must contain 8-160 characters")
        return service.indexing.submit(who, kb_id.hex, body, idempotency=idem)

    @app.get("/api/v1/jobs")
    def jobs(who=Depends(admin)):
        return service.indexing.list(who)

    @app.post("/api/v1/jobs/{job_id}/retry", status_code=202)
    def retry(job_id: UUID, who=Depends(admin)):
        return service.indexing.retry(who, job_id.hex)

    @app.post("/api/v1/jobs/{job_id}/control")
    def control(job_id: UUID, body: JobControlRequest, who=Depends(admin)):
        return service.indexing.control(who, job_id.hex, body.action)

    return app

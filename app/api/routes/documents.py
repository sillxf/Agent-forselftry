from pathlib import Path
from uuid import UUID
import os, tempfile
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from fastapi.responses import FileResponse
from app.api.schemas.knowledge import DocumentPatch, Validity, RestoreVersion


def create_router(service, actor, admin, application):
    app = APIRouter()

    @app.get("/api/v1/knowledge-bases/{kb_id}/documents")
    def documents(kb_id: UUID, who=Depends(actor)):
        return service.inspection.documents(who, kb_id.hex)

    @app.get("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}")
    def document(
        kb_id: UUID,
        document_id: UUID,
        generation_id: str | None = None,
        offset: int = Query(0, ge=0),
        limit: int = Query(50, ge=1, le=100),
        who=Depends(actor),
    ):
        return service.inspection.document(
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
        return service.inspection.chunk(
            who, kb_id.hex, str(chunk_id), generation_id=generation_id
        )

    @app.post("/api/v1/knowledge-bases/{kb_id}/documents", status_code=201)
    async def upload(
        kb_id: UUID,
        request: Request,
        filename: str = Query(..., min_length=1, max_length=180),
        document_id: UUID | None = None,
        who=Depends(admin),
    ):
        limit = int(os.getenv("RAG_UPLOAD_MAX_BYTES", str(25 * 1024 * 1024)))
        size = 0
        temporary = None
        try:
            directory = service.documents.upload_directory(who, kb_id.hex)
            with tempfile.NamedTemporaryFile(
                dir=directory, suffix=".upload", delete=False
            ) as stream:
                temporary = Path(stream.name)
                async for block in request.stream():
                    size += len(block)
                    if size > limit:
                        raise HTTPException(413, "Document exceeds upload size limit")
                    stream.write(block)
            return service.documents.upload(
                who, kb_id.hex, filename, temporary, document_id
            )
        finally:
            if temporary:
                temporary.unlink(missing_ok=True)

    @app.patch("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}")
    def patch_document(
        kb_id: UUID, document_id: UUID, body: DocumentPatch, who=Depends(admin)
    ):
        return service.documents.configure(
            who,
            kb_id.hex,
            str(document_id),
            metadata=body.metadata,
            view_config=body.view_config.model_dump() if body.view_config else None,
        )

    @app.put("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/validity")
    def validity(kb_id: UUID, document_id: UUID, body: Validity, who=Depends(admin)):
        return service.documents.validity(
            who, kb_id.hex, str(document_id), **body.model_dump()
        )

    @app.delete("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}")
    def delete(
        kb_id: UUID, document_id: UUID, confirm: bool = Query(False), who=Depends(admin)
    ):
        if not confirm:
            raise ValueError(
                "Permanent deletion requires confirm=true; use POST .../trash for recoverable removal"
            )
        return service.indexing.delete_document(who, kb_id.hex, str(document_id))

    @app.post("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/trash")
    def trash(kb_id: UUID, document_id: UUID, who=Depends(admin)):
        return service.documents.deleted(who, kb_id.hex, str(document_id))

    @app.post("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/undelete")
    def undelete(kb_id: UUID, document_id: UUID, who=Depends(admin)):
        return service.documents.deleted(who, kb_id.hex, str(document_id), False)

    @app.post("/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/restore-version")
    def restore_version(
        kb_id: UUID, document_id: UUID, body: RestoreVersion, who=Depends(admin)
    ):
        return service.documents.restore(
            who, kb_id.hex, str(document_id), str(body.version_id)
        )

    @app.get(
        "/api/v1/knowledge-bases/{kb_id}/documents/{document_id}/original/{version_id}"
    )
    def original(kb_id: UUID, document_id: UUID, version_id: UUID, who=Depends(actor)):
        path, filename = service.documents.download(
            who, kb_id.hex, str(document_id), str(version_id)
        )
        return FileResponse(
            path, filename=filename, media_type="application/octet-stream"
        )

    return app

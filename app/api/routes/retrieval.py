from fastapi import APIRouter, Depends
from app.core.contracts import SearchRequest, SearchResponse


def create_router(service, actor, admin, application):
    app = APIRouter()

    @app.post(
        "/api/v1/search",
        response_model=SearchResponse,
        response_model_exclude_unset=True,
    )
    def search(body: SearchRequest, who=Depends(actor)):
        return service.retrieval.search(who, body)

    return app

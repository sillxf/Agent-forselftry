import json
from pathlib import Path
from typing import Literal
from fastapi import FastAPI, HTTPException
from app.schemas.alert import Alert
from app.services.alert_deduplicator import (
    deduplicate_alerts
)
from app.services.risk_analyzer import (
    analyze_alert
)
from fastapi import FastAPI, Query
from app.rag.vector_store import VectorStore
from app.rag.embedder import embed_texts
from app.rag.loader import load_documents
from app.rag.retriever import KnowledgeRetriever
from app.services.investigation_service import (
    InvestigationService
)
from app.llm.client import LLMClient
from app.config import *


llm = LLMClient(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
    model=LLM_MODEL
)

knowledge_retriever = KnowledgeRetriever()

investigation_service = InvestigationService(
    knowledge_retriever,
    llm
)

app = FastAPI(
    title="AI-SecOps-Agent",
    description="An AI-assisted security alert investigation system",
    version="0.1.0",
)

DATA_FILE = (
    Path(__file__).parent
    / "data"
    / "sample_alerts.json"
)

Severity = Literal["low", "medium", "high", "critical"]

def load_alerts() -> list[Alert]:
    """Load and validate the sample alert data."""
    raw_data = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    return [Alert.model_validate(item) for item in raw_data]

@app.get("/knowledge/search")
def search_knowledge(
    q: str = Query(
        ...,
        description="Question or keyword"
    ),
    k: int = 3
):

    results = knowledge_retriever.search(
        q,
        k
    )


    return {
        "query": q,
        "results": results
    }

@app.get("/health")
def health_check() -> dict[str, str]:
    return {"status": "ok", "service": "AI-SecOps-Agent"}


@app.get("/alerts", response_model=list[Alert])
def list_alerts(
    severity: Severity | None = None,
) -> list[Alert]:
    """List all alerts, optionally filtered by severity."""
    alerts = load_alerts()

    if severity is not None:
        alerts = [
            alert
            for alert in alerts
            if alert.severity == severity
        ]

    return alerts

@app.get(
"/alerts/deduplicated",
response_model=list[Alert]
)
def deduplicate():

    alerts = load_alerts()

    return deduplicate_alerts(
        alerts
    )

@app.get("/alerts/{alert_id}", response_model=Alert)
def get_alert(alert_id: str) -> Alert:
    """Get one alert by its ID."""
    for alert in load_alerts():
        if alert.id == alert_id:
            return alert

    raise HTTPException(
        status_code=404,
        detail=f"Alert '{alert_id}' not found",
    )



@app.get(
"/alerts/{alert_id}/risk"
)
def risk_analysis(
    alert_id:str
):

    alerts=load_alerts()


    for alert in alerts:

        if alert.id==alert_id:

            return analyze_alert(
                alert
            )


    return {
        "error":
        "not found"
    }

@app.post(
    "/analyze/{alert_id}"
)
def analyze_alert_endpoint(
    alert_id:str
):

    alerts = load_alerts()


    for alert in alerts:

        if alert.id == alert_id:

            result = (
                investigation_service.investigate(alert)
            )


            return result


    raise HTTPException(
        status_code=404
    )
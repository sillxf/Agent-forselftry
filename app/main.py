import sqlite3
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
from app.llm.client import LLMClient
from app.config import *
from pydantic import ValidationError
from app.llm.error import (
    LLMConfigurationError,
    LLMRequestError,
    LLMResponseError,
)
from app.services.output_parser import AnalysisJSONError
from app.services.investigation_service import (
    InvestigationService,
    ToolCallLimitError,
)



llm = LLMClient(
    api_key=LLM_API_KEY,
    base_url=LLM_BASE_URL,
    model=LLM_MODEL
)

if os.getenv("RAG_SERVICE_URL"):
    from rag_service.client import RAGClient
    knowledge_retriever = RAGClient()
elif os.getenv("RAG_EMBEDDED_MODE", "false").lower() == "true":
    from app.rag.retriever import KnowledgeRetriever
    knowledge_retriever = KnowledgeRetriever(build=False, auto_build=False)
else:
    class UnconfiguredKnowledge:
        def search(self, *args, **kwargs):
            raise RuntimeError("Configure RAG_SERVICE_URL/TOKEN/KNOWLEDGE_BASES or explicitly enable RAG_EMBEDDED_MODE")
    knowledge_retriever = UnconfiguredKnowledge()


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

from fastapi.staticfiles import StaticFiles

if os.getenv("RAG_EMBEDDED_MODE", "false").lower() == "true" and not os.getenv("RAG_SERVICE_URL"):
    from app.api.knowledge import create_knowledge_router
    app.include_router(create_knowledge_router(knowledge_retriever, search_provider=lambda: knowledge_retriever))
app.mount("/knowledge/assets", StaticFiles(directory=Path(__file__).parent / "static/knowledge"), name="knowledge-assets")

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
            try:
                result = investigation_service.investigate(
                    alert,
                    alert_pool=alerts,
                )

            except (OSError, sqlite3.DatabaseError) as exc:
                raise HTTPException(status_code=503, detail="Knowledge storage unavailable.") from exc

            except LLMConfigurationError as exc:
                raise HTTPException(
                    status_code=503,
                    detail="LLM service is not configured.",
                ) from exc

            except LLMRequestError as exc:
                raise HTTPException(
                    status_code=502,
                    detail="LLM service request failed.",
                ) from exc  

            except LLMResponseError as exc:
                raise HTTPException(
                    status_code=502,
                    detail="LLM service returned an unusable response.",
                ) from exc

            except AnalysisJSONError as exc:
                raise HTTPException(
                    status_code=502,
                    detail="LLM response was not valid JSON.",
                ) from exc

            except ValidationError as exc:
                raise HTTPException(
                    status_code=502,
                    detail="LLM response did not match the analysis schema.",
                ) from exc

            except ValueError as exc:
                raise HTTPException(status_code=503, detail="Knowledge index unavailable; explicitly build or migrate it first.") from exc

            except ToolCallLimitError as exc:
                raise HTTPException(
                    status_code=502,
                    detail="LLM exceeded the tool-call limit.",
                ) from exc

            except RuntimeError as exc:
                raise HTTPException(status_code=503, detail="Knowledge service unavailable.") from exc

            return result

    raise HTTPException(
        status_code=404
    )
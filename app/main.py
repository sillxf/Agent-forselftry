import json
from pathlib import Path
from typing import Literal

from fastapi import FastAPI, HTTPException

from app.schemas.alert import Alert


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
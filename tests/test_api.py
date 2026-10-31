"""Regression coverage for the original alert and analysis HTTP endpoints."""
from unittest.mock import Mock

from fastapi.testclient import TestClient
import pytest

import app.main as main
from app.llm.error import LLMConfigurationError, LLMRequestError


@pytest.fixture
def client():
    return TestClient(main.app)


def test_health_check(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok", "service": "AI-SecOps-Agent"}


def test_list_and_filter_alerts(client):
    alerts = client.get("/alerts").json()
    assert len(alerts) == 4 and alerts[0]["id"] == "AL-001"
    response = client.get("/alerts", params={"severity": "high"})
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert all(alert["severity"] == "high" for alert in response.json())
    assert client.get("/alerts", params={"severity": "invalid"}).status_code == 422


def test_get_alert_and_missing_id(client):
    response = client.get("/alerts/AL-001")
    assert response.status_code == 200
    assert response.json()["asset_id"] == "srv-web-01"
    assert client.get("/alerts/NOT-FOUND").status_code == 404
    assert client.post("/analyze/NOT-FOUND").status_code == 404


def test_risk_and_deduplication(client):
    response = client.get("/alerts/AL-001/risk")
    assert response.status_code == 200
    assert response.json() == {"alert_id": "AL-001", "risk_score": 80, "priority": "normal"}
    deduplicated = client.get("/alerts/deduplicated")
    assert deduplicated.status_code == 200 and len(deduplicated.json()) == 3


def test_analyze_alert_with_local_dependencies(client, monkeypatch, analysis_service):
    monkeypatch.setattr(main, "investigation_service", analysis_service)
    response = client.post("/analyze/AL-001")
    assert response.status_code == 200
    result = response.json()
    assert result["alert"]["id"] == "AL-001"
    assert result["risk"]["risk_score"] == 80
    assert result["knowledge"]
    assert result["analysis"]["attack_type"] == "mock_analysis"
    assert result["analysis"]["confidence"] == 0.0
    assert "error" not in result["analysis"]


@pytest.mark.parametrize("error,status", [(LLMConfigurationError("not configured"), 503),
                                         (LLMRequestError("upstream failure"), 502)])
def test_analysis_service_errors_are_http_errors(client, monkeypatch, error, status):
    service = Mock()
    service.investigate.side_effect = error
    monkeypatch.setattr(main, "investigation_service", service)
    assert client.post("/analyze/AL-001").status_code == status

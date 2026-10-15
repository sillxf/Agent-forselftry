from fastapi.testclient import TestClient

from app.main import app, investigation_service
from app.llm.client import MockLLM


client = TestClient(app)


def test_health_check():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_list_all_alerts():
    response = client.get("/alerts")

    assert response.status_code == 200

    alerts = response.json()
    assert len(alerts) == 4
    assert alerts[0]["id"] == "AL-001"


def test_filter_high_severity_alerts():
    response = client.get("/alerts?severity=high")

    assert response.status_code == 200

    alerts = response.json()
    assert len(alerts) == 2
    assert all(
        alert["severity"] == "high"
        for alert in alerts
    )


def test_get_alert_by_id():
    response = client.get("/alerts/AL-001")

    assert response.status_code == 200
    assert response.json()["asset_id"] == "srv-web-01"


def test_missing_alert_returns_404():
    response = client.get("/alerts/NOT-FOUND")

    assert response.status_code == 404
    
def test_risk_analysis():
    response = client.get("/alerts/AL-001/risk")

    assert response.status_code == 200
    assert response.json() == {
        "alert_id": "AL-001",
        "risk_score": 80,
        "priority": "normal",
    }


def test_analyze_alert_with_mock(monkeypatch):
    monkeypatch.setattr(
        investigation_service,
        "llm",
        MockLLM(),
    )

    response = client.post("/analyze/AL-001")

    assert response.status_code == 200

    result = response.json()

    assert result["alert"]["id"] == "AL-001"
    assert result["risk"]["risk_score"] == 80
    assert result["knowledge"]
    assert result["analysis"]["attack_type"] == "mock_analysis"
    assert result["analysis"]["confidence"] == 0.0
    assert "error" not in result["analysis"]
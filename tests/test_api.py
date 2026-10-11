from fastapi.testclient import TestClient

from app.main import app


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
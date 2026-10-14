from app.main import (
    investigation_service,
    load_alerts
)


def test_investigation():


    alerts = load_alerts()


    result = (
        investigation_service
        .investigate(
            alerts[0]
        )
    )


    assert "risk" in result

    assert "knowledge" in result

    assert len(
        result["knowledge"]
    ) > 0
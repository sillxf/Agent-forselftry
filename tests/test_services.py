from app.main import load_alerts

from app.services.alert_deduplicator import (
    deduplicate_alerts
)

from app.services.risk_analyzer import (
    analyze_alert
)

def test_alert_deduplication():

    alerts=load_alerts()

    result=deduplicate_alerts(
        alerts
    )


    assert len(result)==3


    from app.services.risk_analyzer import (
    analyze_alert
)


def test_risk():

    alert=load_alerts()[0]


    result=analyze_alert(
        alert
    )


    assert (
        result["risk_score"]
        >0
    )
from app.services.alert_deduplicator import (
    deduplicate_alerts
)

from app.services.risk_analyzer import (
    analyze_alert
)


def search_alerts(
    alerts,
    severity=None
):

    if severity:

        return [
            a for a in alerts
            if a.severity==severity
        ]

    return alerts



def analyze_security_alert(
    alert
):

    return analyze_alert(
        alert
    )
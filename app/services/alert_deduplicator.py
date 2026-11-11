from app.schemas.alert import Alert


def generate_alert_signature(
    alert: Alert
) -> str:
    """
    Generate fingerprint.
    """

    return (
        f"{alert.source}"
        f"-{alert.source_ip}"
        f"-{alert.asset_id}"
        f"-{alert.title}"
    )


def deduplicate_alerts(
    alerts: list[Alert]
) -> list[Alert]:

    seen = set()

    result = []

    for alert in alerts:

        signature = generate_alert_signature(
            alert
        )

        if signature not in seen:
            seen.add(signature)
            result.append(alert)

    return result
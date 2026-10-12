from app.schemas.alert import Alert


def normalize_alert(alert: Alert) -> Alert:
    """
    Normalize alert fields.
    """

    alert.title = alert.title.strip()

    alert.tags = [
        tag.lower()
        for tag in alert.tags
    ]

    return alert
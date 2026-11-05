"""Deterministic triage: rule-based risk score and duplicate grouping. No model."""

from agent.schemas import Alert

SEVERITY_SCORE = {"low": 10, "medium": 30, "high": 70, "critical": 90}


def risk(alert: Alert, related: list[Alert]) -> dict:
    """A transparent prior for prioritising review, not a verdict on the attack.

    Every point added is listed in `factors`, so the model and the analyst can see
    exactly why the score is what it is.
    """
    score, factors = SEVERITY_SCORE[alert.severity], [f"severity={alert.severity}"]
    tags = {t.lower() for t in alert.tags}
    if "authentication" in tags:
        score += 10
        factors.append("authentication-related")
    peers = [
        a
        for a in related
        if a.id != alert.id and alert.source_ip and a.source_ip == alert.source_ip
    ]
    if peers:
        score += 10
        factors.append(f"{len(peers)} other alert(s) from the same source_ip")
    score = min(score, 100)
    return {
        "alert_id": alert.id,
        "risk_score": score,
        "priority": "urgent" if score >= 80 else "normal",
        "factors": factors,
        "note": "Rule-based prior from alert fields; it does not confirm an attack.",
    }


def signature(alert: Alert) -> tuple:
    return (alert.source, alert.source_ip, alert.asset_id, alert.title.strip().lower())


def duplicates(alert: Alert, pool: list[Alert]) -> list[str]:
    """IDs of other alerts with the same signature (same source, IP, asset, title)."""
    key = signature(alert)
    return [a.id for a in pool if a.id != alert.id and signature(a) == key]

import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.schemas.alert import Alert
from app.tools.alert_tools import (
    execute_alert_tool,
    ToolExecutionError,
)


def load_sample_alerts():
    path = (
        Path(__file__).resolve().parents[1]
        / "app"
        / "data"
        / "sample_alerts.json"
    )

    raw_data = json.loads(
        path.read_text(encoding="utf-8")
    )

    return [
        Alert.model_validate(item)
        for item in raw_data
    ]


def test_search_alerts_filters_by_severity():
    alerts = load_sample_alerts()

    result = execute_alert_tool(
        tool_name="search_alerts",
        arguments={
            "severity": "high",
        },
        alerts=alerts,
    )

    assert len(result) == 2
    assert all(
        item["severity"] == "high"
        for item in result
    )


def test_search_alerts_rejects_invalid_severity():
    alerts = load_sample_alerts()

    with pytest.raises(ValidationError):
        execute_alert_tool(
            tool_name="search_alerts",
            arguments={
                "severity": "extreme",
            },
            alerts=alerts,
        )


def test_analyze_alert_by_id():
    alerts = load_sample_alerts()

    result = execute_alert_tool(
        tool_name="analyze_security_alert",
        arguments={
            "alert_id": "AL-001",
        },
        alerts=alerts,
    )

    assert result["alert_id"] == "AL-001"
    assert "risk_score" in result


def test_unknown_tool_is_rejected():
    alerts = load_sample_alerts()

    with pytest.raises(ToolExecutionError):
        execute_alert_tool(
            tool_name="delete_alerts",
            arguments={},
            alerts=alerts,
        )
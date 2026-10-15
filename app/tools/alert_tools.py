from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from app.schemas.alert import Alert
from app.services.risk_analyzer import analyze_alert


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

class SearchAlertsArguments(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    severity: Literal[
        "low",
        "medium",
        "high",
        "critical",
    ] | None = None


class AnalyzeAlertArguments(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    alert_id: str = Field(
        min_length=1
    )


ALERT_TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_alerts",
            "description": (
                "Search available security alerts, "
                "optionally filtered by severity."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "severity": {
                        "type": "string",
                        "enum": [
                            "low",
                            "medium",
                            "high",
                            "critical",
                        ],
                    }
                },
                "required": [],
                "additionalProperties": False,
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "analyze_security_alert",
            "description": (
                "Calculate the risk information "
                "for an alert identified by its ID."
            ),
            "parameters": {
                "type": "object",
                "properties": {
                    "alert_id": {
                        "type": "string",
                        "minLength": 1,
                    }
                },
                "required": ["alert_id"],
                "additionalProperties": False,
            },
        },
    },
]


##执行器
class ToolExecutionError(RuntimeError):
    """工具名称或执行目标无效。"""


def execute_alert_tool(
    tool_name: str,
    arguments: dict,
    alerts: list[Alert],
) -> dict | list[dict]:

    if not isinstance(arguments, dict):
        raise ToolExecutionError(
            "Tool arguments must be a JSON object."
        )

    if tool_name == "search_alerts":
        parsed = SearchAlertsArguments.model_validate(
            arguments
        )

        matches = search_alerts(
            alerts,
            severity=parsed.severity,
        )

        return [
            alert.model_dump(mode="json")
            for alert in matches
        ]

    if tool_name == "analyze_security_alert":
        parsed = AnalyzeAlertArguments.model_validate(
            arguments
        )

        alert = next(
            (
                item
                for item in alerts
                if item.id == parsed.alert_id
            ),
            None,
        )

        if alert is None:
            raise ToolExecutionError(
                f"Alert '{parsed.alert_id}' was not found."
            )

        return analyze_security_alert(alert)

    raise ToolExecutionError(
        f"Tool '{tool_name}' is not allowed."
    )
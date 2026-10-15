import copy
import json
from pathlib import Path

import pytest

from app.schemas.alert import Alert
from app.services.investigation_service import (
    InvestigationService,
    ToolCallLimitError,
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


class FakeRetriever:
    def search(self, query, k=3):
        return [
            {
                "source": "brute_force.md",
                "content": (
                    "Repeated failed login attempts "
                    "may indicate brute force activity."
                ),
            }
        ]


class ScriptedLLM:
    def __init__(self, responses):
        self.responses = list(responses)
        self.calls = []

    def chat(self, messages, tools=None):
        self.calls.append(
            {
                "messages": copy.deepcopy(messages),
                "tools": copy.deepcopy(tools),
            }
        )

        if not self.responses:
            raise AssertionError(
                "No scripted LLM response remains."
            )

        return self.responses.pop(0)


def test_tool_call_loop_executes_and_returns_tool_result():
    alerts = load_sample_alerts()

    arguments = json.dumps(
        {
            "severity": "high",
        }
    )

    assistant_tool_message = {
        "role": "assistant",
        "tool_calls": [
            {
                "id": "call_001",
                "type": "function",
                "function": {
                    "name": "search_alerts",
                    "arguments": arguments,
                },
            }
        ],
    }

    final_json = json.dumps(
        {
            "attack_type": "brute_force",
            "confidence": 0.92,
            "evidence": [
                "Multiple failed login attempts"
            ],
            "recommendations": [
                "Investigate the source IP"
            ],
        }
    )

    llm = ScriptedLLM(
        [
            {
                "content": None,
                "tool_calls": [
                    {
                        "id": "call_001",
                        "name": "search_alerts",
                        "arguments": arguments,
                    }
                ],
                "assistant_message": (
                    assistant_tool_message
                ),
            },
            {
                "content": final_json,
                "tool_calls": [],
                "assistant_message": {
                    "role": "assistant",
                    "content": final_json,
                },
            },
        ]
    )

    service = InvestigationService(
        retriever=FakeRetriever(),
        llm=llm,
    )

    result = service.investigate(
        alert=alerts[0],
        alert_pool=alerts,
    )

    assert result["analysis"].attack_type == "brute_force"
    assert len(llm.calls) == 2

    second_call_messages = (
        llm.calls[1]["messages"]
    )

    tool_messages = [
        item
        for item in second_call_messages
        if item["role"] == "tool"
    ]

    assert len(tool_messages) == 1
    assert tool_messages[0]["tool_call_id"] == "call_001"

    tool_output = json.loads(
        tool_messages[0]["content"]
    )

    assert tool_output["ok"] is True
    assert len(tool_output["result"]) == 2


def test_tool_call_loop_stops_after_maximum_rounds():
    alerts = load_sample_alerts()

    responses = []

    for index in range(4):
        call_id = f"call_{index}"

        arguments = json.dumps(
            {
                "severity": "high",
            }
        )

        responses.append(
            {
                "content": None,
                "tool_calls": [
                    {
                        "id": call_id,
                        "name": "search_alerts",
                        "arguments": arguments,
                    }
                ],
                "assistant_message": {
                    "role": "assistant",
                    "tool_calls": [
                        {
                            "id": call_id,
                            "type": "function",
                            "function": {
                                "name": "search_alerts",
                                "arguments": arguments,
                            },
                        }
                    ],
                },
            }
        )

    llm = ScriptedLLM(responses)

    service = InvestigationService(
        retriever=FakeRetriever(),
        llm=llm,
    )

    with pytest.raises(ToolCallLimitError):
        service.investigate(
            alert=alerts[0],
            alert_pool=alerts,
        )
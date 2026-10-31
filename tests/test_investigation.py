import json
from unittest.mock import Mock

from app.main import load_alerts
from app.services.investigation_service import InvestigationService


def test_investigation(rag_factory):
    (rag_factory.knowledge / "brute_force.md").write_text(
        "# Brute Force\n\nMultiple failed login attempts. Block suspicious IP and enable MFA.", encoding="utf-8")
    llm = Mock()
    llm.chat.return_value = {
        "content": json.dumps({"attack_type": "brute_force", "confidence": .9,
                               "evidence": ["Multiple failed login attempts"],
                               "recommendations": ["Enable MFA"]}),
        "tool_calls": [],
    }
    service = InvestigationService(rag_factory(build=False), llm)
    result = service.investigate(load_alerts()[0])
    assert "risk" in result
    assert result["knowledge"]
    assert result["knowledge"][0]["source"] == "brute_force.md"
    assert result["knowledge"][0]["chunk_id"]
    assert "Multiple failed login attempts" in llm.chat.call_args.kwargs["messages"][0]["content"]

    prompt = llm.chat.call_args.kwargs["messages"][0]["content"]
    assert "untrusted reference data" in prompt
    assert result["knowledge"][0]["chunk_id"] in prompt

from app.main import load_alerts
from app.schemas.analysis import SecurityAnalysis


def test_investigation_returns_typed_analysis_and_evidence(analysis_service):
    result = analysis_service.investigate(load_alerts()[0])
    assert result["knowledge"]
    analysis = result["analysis"]
    assert isinstance(analysis, SecurityAnalysis)
    assert analysis.attack_type == "mock_analysis"
    assert analysis.confidence == 0.0
    prompt = analysis_service.llm.chat.call_args.kwargs["messages"][0]["content"]
    assert result["knowledge"][0]["chunk_id"] in prompt
    assert "untrusted reference data" in prompt

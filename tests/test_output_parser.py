import pytest

from pydantic import ValidationError

from app.schemas.analysis import SecurityAnalysis
from app.services.output_parser import (
    AnalysisJSONError,
    parse_analysis,
)


def test_parse_valid_analysis():
    text = """
    {
        "attack_type": "brute_force",
        "confidence": 0.92,
        "evidence": ["Repeated failed logins"],
        "recommendations": ["Review the source IP"]
    }
    """

    result = parse_analysis(text)

    assert isinstance(result, SecurityAnalysis)
    assert result.attack_type == "brute_force"
    assert result.confidence == 0.92


def test_invalid_json_raises_analysis_json_error():
    with pytest.raises(AnalysisJSONError):
        parse_analysis(
            '{"attack_type": "brute_force"'
        )


def test_invalid_confidence_raises_validation_error():
    text = """
    {
        "attack_type": "brute_force",
        "confidence": 1.8,
        "evidence": [],
        "recommendations": []
    }
    """

    with pytest.raises(ValidationError):
        parse_analysis(text)
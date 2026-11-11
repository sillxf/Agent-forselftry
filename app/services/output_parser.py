import json

from app.schemas.analysis import SecurityAnalysis


class AnalysisJSONError(ValueError):
    """LLM 返回内容不是有效 JSON。"""


def parse_analysis(
    text: str
) -> SecurityAnalysis:
    if not isinstance(text, str) or not text.strip():
        raise AnalysisJSONError(
            "Analysis text is empty or is not a string."
        )

    try:
        data = json.loads(text)
    except json.JSONDecodeError as exc:
        raise AnalysisJSONError(
            "Analysis text is not valid JSON."
        ) from exc

    return SecurityAnalysis.model_validate(data)
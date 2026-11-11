from pydantic import BaseModel, Field, ConfigDict


class SecurityAnalysis(BaseModel):
    model_config = ConfigDict(
        extra="forbid"
    )

    attack_type: str

    confidence: float = Field(
        ge=0.0,
        le=1.0
    )

    evidence: list[str]

    recommendations: list[str]
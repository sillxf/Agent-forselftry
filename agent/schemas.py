"""Typed inputs and outputs of an investigation. The final report is code-verified."""

from datetime import datetime
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

Severity = Literal["low", "medium", "high", "critical"]
ClaimType = Literal[
    "observed_event", "reference_knowledge", "supported_inference", "unverified_hypothesis"
]


class Alert(BaseModel):
    model_config = ConfigDict(extra="forbid")
    id: str = Field(min_length=1, max_length=200)
    detected_at: datetime
    source: str = Field(min_length=1, max_length=200)
    severity: Severity
    title: str = Field(min_length=1, max_length=500)
    source_ip: str | None = Field(None, max_length=100)
    destination_ip: str | None = Field(None, max_length=100)
    asset_id: str = Field(min_length=1, max_length=200)
    description: str = Field(max_length=8000)
    tags: list[str] = Field(default_factory=list, max_length=50)


class Hypothesis(BaseModel):
    model_config = ConfigDict(extra="forbid")
    label: str = Field(min_length=1, max_length=300)
    status: Literal["confirmed", "suspected", "unconfirmed"]
    confidence: float = Field(ge=0.0, le=1.0)


class Claim(BaseModel):
    model_config = ConfigDict(extra="forbid")
    type: ClaimType
    text: str = Field(min_length=1, max_length=2000)
    sources: list[str] = Field(default_factory=list, max_length=20)


class Recommendation(BaseModel):
    model_config = ConfigDict(extra="forbid")
    action: str = Field(min_length=1, max_length=1000)
    priority: Literal["high", "medium", "low"]
    # The agent has read-only tools; a recommendation is never an executed action.
    executed: Literal[False] = False


class ModelReport(BaseModel):
    """What the model must return. Extra keys are rejected."""

    model_config = ConfigDict(extra="forbid")
    summary: str = Field(min_length=1, max_length=4000)
    attack_hypothesis: Hypothesis
    claims: list[Claim] = Field(min_length=1, max_length=40)
    gaps: list[str] = Field(default_factory=list, max_length=20)
    recommendations: list[Recommendation] = Field(default_factory=list, max_length=20)


class Downgrade(BaseModel):
    claim_index: int
    original_type: ClaimType
    reason: str


class Verification(BaseModel):
    downgraded: list[Downgrade] = Field(default_factory=list)
    unknown_sources: list[str] = Field(default_factory=list)
    hypothesis_adjusted: str | None = None


class Report(ModelReport):
    model_config = ConfigDict(extra="forbid")
    verification: Verification

from pydantic import BaseModel
from typing import List

class SecurityAnalysis(BaseModel):

    attack_type: str

    confidence: float

    evidence: List[str]

    recommendations: List[str]
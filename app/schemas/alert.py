from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


class Alert(BaseModel):
    id: str = Field(min_length=1)
    detected_at: datetime
    source: str
    severity: Literal["low", "medium", "high", "critical"]
    title: str
    source_ip: str | None = None
    destination_ip: str | None = None
    asset_id: str
    description: str
    tags: list[str] = Field(default_factory=list)
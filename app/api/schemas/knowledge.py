from uuid import UUID
from pydantic import BaseModel, ConfigDict
from app.indexing.views import ViewConfig


class DocumentPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")
    metadata: dict[str, str] | None = None
    view_config: ViewConfig | None = None


class Validity(BaseModel):
    model_config = ConfigDict(extra="forbid")
    effective_at: str | None = None
    expires_at: str | None = None


class RestoreVersion(BaseModel):
    model_config = ConfigDict(extra="forbid")
    version_id: UUID


class Enabled(BaseModel):
    model_config = ConfigDict(extra="forbid")
    enabled: bool

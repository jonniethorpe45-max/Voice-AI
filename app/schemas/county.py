from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import CountyKey


class CountyConfigBase(BaseModel):
    state: str
    county_name: str
    county_key: CountyKey
    sale_type: str
    source_urls_json: list[str] = Field(default_factory=list)
    assignment_supported: bool = False
    assignment_confidence: float = Field(default=0.0, ge=0.0, le=1.0)
    manual_review_required: bool = True
    active_for_ingestion: bool = True
    active_for_outreach: bool = False
    notes: str | None = None


class CountyConfigCreate(CountyConfigBase):
    pass


class CountyConfigUpdate(BaseModel):
    sale_type: str | None = None
    source_urls_json: list[str] | None = None
    assignment_supported: bool | None = None
    assignment_confidence: float | None = Field(default=None, ge=0.0, le=1.0)
    manual_review_required: bool | None = None
    active_for_ingestion: bool | None = None
    active_for_outreach: bool | None = None
    notes: str | None = None


class CountyConfigResponse(CountyConfigBase):
    model_config = ConfigDict(from_attributes=True)
    id: int

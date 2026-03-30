from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field

from app.models.enums import LeadStatus, LobVerificationStatus


class LeadOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    state: str
    county: str
    owner_name: str
    mailing_address: str | None
    property_address: str | None
    parcel_number: str | None
    sale_date: date | None
    surplus_amount: Decimal | None
    status: LeadStatus
    lob_verification_status: LobVerificationStatus
    manual_review_required: bool
    legal_review_cleared: bool
    assignment_confidence: float
    source_url: str | None
    notes: str | None
    source_hash: str | None
    quality_score: float
    probate_risk: bool
    duplicate_owner: bool
    duplicate_property: bool
    florida_manual_only: bool
    california_assignment_possible: bool
    extraction_metadata: dict | None
    created_at: datetime
    updated_at: datetime


class LeadListResponse(BaseModel):
    items: list[LeadOut]
    pagination: dict[str, int]


class LeadUpdateNotes(BaseModel):
    notes: str


class LegalReviewClearRequest(BaseModel):
    legal_review_cleared: bool = True


class LeadNoteCreate(BaseModel):
    note: str = Field(min_length=1, max_length=4000)


class LeadNoteResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    note: str
    created_by_user_id: int | None
    created_at: datetime


class LeadTimelineEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    event_type: str
    payload: dict | None
    created_at: datetime


class LeadTimelineResponse(BaseModel):
    items: list[LeadTimelineEvent]

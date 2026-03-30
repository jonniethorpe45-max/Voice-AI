from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import TrackingStatus


class TrackingEventCreate(BaseModel):
    lead_id: int
    letter_id: int | None = None
    status: TrackingStatus
    external_id: str | None = None
    details: str | None = None
    event_time: datetime | None = None


class TrackingEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    letter_id: int | None
    status: TrackingStatus
    external_id: str | None
    details: str | None
    event_time: datetime


class TrackingListResponse(BaseModel):
    items: list[TrackingEventOut]

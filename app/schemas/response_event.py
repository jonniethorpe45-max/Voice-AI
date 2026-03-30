from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import ResponseChannel


class ResponseEventCreate(BaseModel):
    lead_id: int
    channel: ResponseChannel
    payload: dict
    operator_note: str | None = None


class ResponseEventOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    channel: str
    payload_json: dict
    operator_note: str | None = None
    created_at: datetime

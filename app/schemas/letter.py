from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.models.enums import LetterTemplateKey


class LetterPreviewRequest(BaseModel):
    lead_id: int
    template_key: LetterTemplateKey


class LetterDecisionRequest(BaseModel):
    note: str | None = None
    hold_reason: str | None = None
    rejection_reason: str | None = None
    send_to_lob: bool = True


class LetterOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int
    template_key: LetterTemplateKey
    status: str
    body: str
    preview_payload: dict | None = None
    lob_letter_id: str | None = None
    rejection_reason: str | None = None
    hold_reason: str | None = None
    approved_by_user_id: int | None = None
    created_at: datetime
    updated_at: datetime


class LetterQueueResponse(BaseModel):
    items: list[LetterOut]
    pagination: dict[str, int]

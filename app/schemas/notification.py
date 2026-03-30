from datetime import datetime

from pydantic import BaseModel, ConfigDict


class NotificationOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    lead_id: int | None
    event_type: str
    message: str
    created_at: datetime

from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin


class ResponseEvent(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "response_events"

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False)
    channel: Mapped[str] = mapped_column(String(20), nullable=False)
    payload_json: Mapped[dict] = mapped_column(JSONB, nullable=False, default=dict)
    operator_note: Mapped[str | None] = mapped_column(Text, nullable=True)

    lead = relationship("Lead", back_populates="response_events")

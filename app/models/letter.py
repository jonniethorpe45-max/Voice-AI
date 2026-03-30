from __future__ import annotations

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin


class Letter(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "letters"

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    template_key: Mapped[str] = mapped_column(String(64), nullable=False)
    status: Mapped[str] = mapped_column(String(32), nullable=False, default="preview", index=True)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    preview_payload: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    lob_letter_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    rejection_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    hold_reason: Mapped[str | None] = mapped_column(Text, nullable=True)
    approved_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)

    lead = relationship("Lead", back_populates="letters")

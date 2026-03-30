from __future__ import annotations

from datetime import date
from decimal import Decimal
from typing import Any

from sqlalchemy import Boolean, Date, Float, ForeignKey, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin
from app.models.enums import LeadStatus, LobVerificationStatus


class Lead(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "leads"

    state: Mapped[str] = mapped_column(String(2), index=True, nullable=False)
    county: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    owner_name: Mapped[str] = mapped_column(String(255), index=True, nullable=False)
    mailing_address: Mapped[str | None] = mapped_column(Text)
    property_address: Mapped[str | None] = mapped_column(Text)
    parcel_number: Mapped[str | None] = mapped_column(String(120), index=True)
    sale_date: Mapped[date | None] = mapped_column(Date)
    surplus_amount: Mapped[Decimal | None] = mapped_column(Numeric(14, 2))
    status: Mapped[str] = mapped_column(String(40), index=True, default=LeadStatus.NEW.value, nullable=False)
    lob_verification_status: Mapped[str] = mapped_column(
        String(40), default=LobVerificationStatus.NOT_STARTED.value, nullable=False
    )
    manual_review_required: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    legal_review_cleared: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    assignment_confidence: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    source_url: Mapped[str | None] = mapped_column(Text)
    notes: Mapped[str | None] = mapped_column(Text)
    source_hash: Mapped[str | None] = mapped_column(String(128), index=True)
    quality_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    probate_risk: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duplicate_owner: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    duplicate_property: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    florida_manual_only: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    california_assignment_possible: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    extraction_metadata: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    tracking_events = relationship("TrackingEvent", back_populates="lead")
    response_events = relationship("ResponseEvent", back_populates="lead")
    letters = relationship("Letter", back_populates="lead")
    notes_items = relationship("LeadNote", back_populates="lead")
    timeline_items = relationship("LeadTimeline", back_populates="lead")
    raw_snapshots = relationship("RawSourceSnapshot", back_populates="lead")


class LeadNote(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "lead_notes"

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False)
    note: Mapped[str] = mapped_column(Text, nullable=False)
    created_by_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"))

    lead = relationship("Lead", back_populates="notes_items")


class LeadTimeline(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "lead_timeline"

    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), index=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), index=True, nullable=False)
    payload: Mapped[dict[str, Any] | None] = mapped_column(JSONB)

    lead = relationship("Lead", back_populates="timeline_items")

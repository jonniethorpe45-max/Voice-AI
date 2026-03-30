from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.models.base import Base


class TrackingEvent(Base):
    __tablename__ = "tracking_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    lead_id: Mapped[int] = mapped_column(ForeignKey("leads.id", ondelete="CASCADE"), nullable=False, index=True)
    letter_id: Mapped[int | None] = mapped_column(ForeignKey("letters.id", ondelete="SET NULL"), nullable=True, index=True)
    status: Mapped[str] = mapped_column(String(24), nullable=False, index=True)
    external_id: Mapped[str | None] = mapped_column(String(128), nullable=True, index=True)
    details: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_time: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False, index=True)

    lead = relationship("Lead", back_populates="tracking_events")
    letter = relationship("Letter")

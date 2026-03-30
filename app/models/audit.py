from __future__ import annotations

from typing import Any

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IntegerPrimaryKeyMixin, TimestampMixin


class AuditLog(Base, IntegerPrimaryKeyMixin, TimestampMixin):
    __tablename__ = "audit_logs"

    actor_user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True)
    actor_label: Mapped[str] = mapped_column(String(255), default="system", nullable=False)
    event_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_type: Mapped[str] = mapped_column(String(80), nullable=False, index=True)
    entity_id: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    summary: Mapped[str | None] = mapped_column(Text, nullable=True)
    metadata_json: Mapped[dict[str, Any] | None] = mapped_column(JSONB, nullable=True)

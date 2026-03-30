from sqlalchemy import Boolean, Float, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin


class CountyConfig(Base, TimestampMixin):
    __tablename__ = "county_configs"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    state: Mapped[str] = mapped_column(String(2), nullable=False, index=True)
    county_name: Mapped[str] = mapped_column(String(120), nullable=False)
    county_key: Mapped[str] = mapped_column(String(40), nullable=False, unique=True, index=True)
    sale_type: Mapped[str] = mapped_column(String(120), nullable=False)
    source_urls_json: Mapped[list[str]] = mapped_column(JSONB, nullable=False, default=list)
    assignment_supported: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    assignment_confidence: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)
    manual_review_required: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active_for_ingestion: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    active_for_outreach: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

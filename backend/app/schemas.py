from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, Field

JobState = Literal["uploaded", "queued", "running", "completed", "failed", "completed_with_warnings"]


def utc_now() -> datetime:
    return datetime.now(timezone.utc)


class StyleControls(BaseModel):
    warmth: float = Field(default=0.5, ge=0.0, le=1.0)
    brightness: float = Field(default=0.5, ge=0.0, le=1.0)
    power: float = Field(default=0.5, ge=0.0, le=1.0)
    breathiness: float = Field(default=0.3, ge=0.0, le=1.0)
    smoothness: float = Field(default=0.6, ge=0.0, le=1.0)
    emotion_intensity: float = Field(default=0.6, ge=0.0, le=1.0)
    soft_pitch_strength: float = Field(default=0.35, ge=0.0, le=1.0)


class UploadResponse(BaseModel):
    job_id: str
    status: JobState
    created_at: datetime = Field(default_factory=utc_now)


class ProcessRequest(BaseModel):
    job_id: str = Field(..., description="Job ID returned by /upload")
    style_controls: StyleControls = Field(default_factory=StyleControls)
    preferred_variations: list[str] = Field(default_factory=list)


class ProcessResponse(BaseModel):
    job_id: str
    status: JobState
    queued_at: datetime = Field(default_factory=utc_now)


class JobStatusResponse(BaseModel):
    job_id: str
    status: JobState
    progress: int = Field(default=0, ge=0, le=100)
    message: str = ""
    updated_at: datetime = Field(default_factory=utc_now)
    error: str | None = None


class VariationResult(BaseModel):
    label: str
    media_url: str
    metadata: dict[str, Any] = Field(default_factory=dict)


class JobResultResponse(BaseModel):
    job_id: str
    status: JobState
    message: str = ""
    variations: list[VariationResult] = Field(default_factory=list)
    analysis: dict[str, Any] = Field(default_factory=dict)

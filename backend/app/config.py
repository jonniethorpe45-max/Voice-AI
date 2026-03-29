from __future__ import annotations

import json
from pathlib import Path

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VocalFit AI API"
    app_version: str = "0.1.0"

    redis_url: str = "redis://localhost:6379/0"
    queue_cpu_name: str = "vocalfit:jobs:cpu"
    queue_gpu_name: str = "vocalfit:jobs:gpu"
    queue_dead_letter_name: str = "vocalfit:jobs:dead"
    job_status_prefix: str = "vocalfit:status:"
    job_ttl_seconds: int = 86400
    queue_block_seconds: int = 2
    max_job_retries: int = 2

    storage_root: Path = Path("./data")
    upload_subdir: str = "uploads"
    output_subdir: str = "outputs"
    model_root: Path = Path("./models")

    use_gpu: bool = False
    use_demucs: bool = True
    worker_capability: str = "cpu"
    max_file_size_mb: int = 150
    allowed_audio_extensions: set[str] = {".wav", ".mp3", ".m4a"}
    cors_origins: list[str] = ["http://localhost:3000", "http://localhost:5173", "http://localhost:8000"]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_prefix="VOCALFIT_",
        extra="ignore",
    )

    @property
    def max_upload_size_bytes(self) -> int:
        return self.max_file_size_mb * 1024 * 1024

    @property
    def upload_dir(self) -> Path:
        return self.storage_root / self.upload_subdir

    @property
    def output_dir(self) -> Path:
        return self.storage_root / self.output_subdir

    @field_validator("worker_capability", mode="before")
    @classmethod
    def validate_worker_capability(cls, value: str) -> str:
        capability = str(value).strip().lower()
        if capability not in {"cpu", "gpu"}:
            return "cpu"
        return capability

    @field_validator("cors_origins", mode="before")
    @classmethod
    def normalize_cors_origins(cls, value: object) -> list[str]:
        if value is None:
            return []
        if isinstance(value, list):
            return [str(item).strip() for item in value if str(item).strip()]
        raw = str(value).strip()
        if not raw:
            return []
        if raw.startswith("["):
            try:
                parsed = json.loads(raw)
                if isinstance(parsed, list):
                    return [str(item).strip() for item in parsed if str(item).strip()]
            except json.JSONDecodeError:
                pass
        return [item.strip() for item in raw.split(",") if item.strip()]

    def ensure_storage(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_root.mkdir(parents=True, exist_ok=True)


settings = Settings()

from __future__ import annotations

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "VocalFit AI API"
    app_version: str = "0.1.0"

    redis_url: str = "redis://redis:6379/0"
    queue_name: str = "vocalfit:jobs"
    job_status_prefix: str = "vocalfit:status:"
    job_ttl_seconds: int = 86400

    storage_root: Path = Path("/app/data")
    upload_subdir: str = "uploads"
    output_subdir: str = "outputs"
    model_root: Path = Path("/app/models")

    use_gpu: bool = True
    use_demucs: bool = True
    max_file_size_mb: int = 150
    allowed_audio_extensions: set[str] = {".wav", ".mp3", ".m4a"}
    cors_origins: list[str] = ["*"]

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

    def ensure_storage(self) -> None:
        self.upload_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.model_root.mkdir(parents=True, exist_ok=True)


settings = Settings()

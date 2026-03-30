from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "Surplus Recovery Ops API"
    environment: Literal["local", "staging", "production"] = "local"
    api_v1_prefix: str = "/api/v1"
    debug: bool = False

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@db:5432/surplus_ops",
        alias="DATABASE_URL",
    )
    redis_url: str = Field(default="redis://redis:6379/0", alias="REDIS_URL")

    jwt_secret_key: str = Field(default="change-me-access-secret", alias="JWT_SECRET_KEY")
    jwt_refresh_secret_key: str = Field(default="change-me-refresh-secret", alias="JWT_REFRESH_SECRET_KEY")
    jwt_algorithm: str = Field(default="HS256", alias="JWT_ALGORITHM")
    jwt_access_token_expire_minutes: int = Field(default=60, alias="JWT_ACCESS_TOKEN_EXPIRE_MINUTES")
    jwt_refresh_token_expire_minutes: int = Field(default=60 * 24 * 14, alias="JWT_REFRESH_TOKEN_EXPIRE_MINUTES")

    seed_admin_email: str = Field(default="admin@surplus.local", alias="SEED_ADMIN_EMAIL")
    seed_admin_password: str = Field(default="admin123456", alias="SEED_ADMIN_PASSWORD")

    lob_api_key: str | None = Field(default=None, alias="LOB_API_KEY")
    lob_base_url: str = Field(default="https://api.lob.com/v1", alias="LOB_BASE_URL")
    twilio_webhook_token: str | None = Field(default=None, alias="TWILIO_WEBHOOK_TOKEN")
    inbound_email_secret: str | None = Field(default=None, alias="INBOUND_EMAIL_SECRET")

    cors_origins: list[str] = Field(default_factory=lambda: ["*"], alias="CORS_ORIGINS")

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, list):
            return value
        return [item.strip() for item in value.split(",") if item.strip()]


@lru_cache
def get_settings() -> Settings:
    return Settings()


settings = get_settings()

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import JWTError, jwt
from passlib.context import CryptContext

from app.core.config import settings

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)


def hash_password(password: str) -> str:
    return pwd_context.hash(password)


def _create_token(
    subject: str,
    *,
    secret: str,
    expires_minutes: int,
    token_type: str,
    extra: dict[str, Any] | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": subject,
        "type": token_type,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=expires_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, secret, algorithm=settings.jwt_algorithm)


def create_access_token(subject: str) -> str:
    return _create_token(
        subject,
        secret=settings.jwt_secret_key,
        expires_minutes=settings.jwt_access_token_expire_minutes,
        token_type="access",
    )


def create_refresh_token(subject: str) -> str:
    return _create_token(
        subject,
        secret=settings.jwt_refresh_secret_key,
        expires_minutes=settings.jwt_refresh_token_expire_minutes,
        token_type="refresh",
    )


def decode_token(token: str, *, expected_type: str | None = None) -> dict[str, Any]:
    last_error: Exception | None = None
    for secret in (settings.jwt_secret_key, settings.jwt_refresh_secret_key):
        try:
            payload = jwt.decode(token, secret, algorithms=[settings.jwt_algorithm])
            if expected_type and payload.get("type") != expected_type:
                raise ValueError("Invalid token type")
            return payload
        except JWTError as exc:
            last_error = exc
            continue
    raise ValueError("Invalid token") from last_error

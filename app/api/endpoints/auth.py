from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.config import settings
from app.core.database import get_db
from app.core.security import create_access_token, create_refresh_token, decode_token, verify_password
from app.models.user import RefreshToken, User
from app.schemas.auth import LoginRequest, RefreshTokenRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth")


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.scalar(select(User).where(User.email == payload.email))
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    access = create_access_token(str(user.id))
    refresh = create_refresh_token(str(user.id))
    db.add(
        RefreshToken(
            user_id=user.id,
            token=refresh,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_refresh_token_expire_minutes),
        )
    )
    db.commit()
    return TokenResponse(
        access_token=access,
        refresh_token=refresh,
        token_type="bearer",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshTokenRequest, db: Session = Depends(get_db)) -> TokenResponse:
    token_row = db.scalar(
        select(RefreshToken).where(RefreshToken.token == payload.refresh_token, RefreshToken.revoked.is_(False))
    )
    if not token_row:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid refresh token")
    if token_row.expires_at <= datetime.now(timezone.utc):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token expired")
    claims = decode_token(payload.refresh_token, expected_type="refresh")
    if str(token_row.user_id) != str(claims.get("sub")):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Refresh token subject mismatch")
    token_row.revoked = True
    access = create_access_token(str(token_row.user_id))
    refresh_new = create_refresh_token(str(token_row.user_id))
    db.add(
        RefreshToken(
            user_id=token_row.user_id,
            token=refresh_new,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_refresh_token_expire_minutes),
        )
    )
    db.commit()
    return TokenResponse(
        access_token=access,
        refresh_token=refresh_new,
        token_type="bearer",
        expires_at=datetime.now(timezone.utc) + timedelta(minutes=settings.jwt_access_token_expire_minutes),
    )


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)

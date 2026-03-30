from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.notification import NotificationOut

router = APIRouter(prefix="/notifications")


@router.get("", response_model=list[NotificationOut])
def list_notifications(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[Notification]:
    return db.scalars(select(Notification).order_by(Notification.created_at.desc())).all()

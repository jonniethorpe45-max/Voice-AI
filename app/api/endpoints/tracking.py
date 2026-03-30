from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import require_active_user
from app.core.database import get_db
from app.models.tracking import TrackingEvent
from app.schemas.tracking import TrackingEventOut, TrackingListResponse

router = APIRouter(prefix="/tracking")


@router.get("", response_model=TrackingListResponse)
def list_tracking(
    lead_id: int | None = None,
    db: Session = Depends(get_db),
    _=Depends(require_active_user),
) -> TrackingListResponse:
    stmt = select(TrackingEvent).order_by(TrackingEvent.event_time.desc())
    if lead_id:
        stmt = stmt.where(TrackingEvent.lead_id == lead_id)
    items = list(db.scalars(stmt))
    return TrackingListResponse(items=[TrackingEventOut.model_validate(i) for i in items])


@router.get("/{tracking_id}", response_model=TrackingEventOut)
def get_tracking(tracking_id: int, db: Session = Depends(get_db), _=Depends(require_active_user)) -> TrackingEventOut:
    event = db.get(TrackingEvent, tracking_id)
    if not event:
        raise HTTPException(status_code=404, detail="Tracking event not found")
    return TrackingEventOut.model_validate(event)

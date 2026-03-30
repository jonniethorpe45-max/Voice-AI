from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.lead import Lead, LeadNote, LeadTimeline
from app.models.user import User
from app.schemas.lead import (
    LeadListResponse,
    LeadNoteCreate,
    LeadNoteResponse,
    LeadOut,
    LeadTimelineEvent,
    LeadTimelineResponse,
    LeadUpdateNotes,
    LegalReviewClearRequest,
)
from app.services.audit import log_audit
from app.services.notifications import create_notification

router = APIRouter(prefix="/leads")


@router.get("", response_model=LeadListResponse)
def list_leads(
    status_filter: str | None = Query(default=None, alias="status"),
    state: str | None = None,
    county: str | None = None,
    q: str | None = None,
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> LeadListResponse:
    stmt = select(Lead)
    if status_filter:
        stmt = stmt.where(Lead.status == status_filter)
    if state:
        stmt = stmt.where(Lead.state == state)
    if county:
        stmt = stmt.where(Lead.county == county)
    if q:
        term = f"%{q}%"
        stmt = stmt.where(
            or_(
                Lead.owner_name.ilike(term),
                Lead.parcel_number.ilike(term),
                Lead.property_address.ilike(term),
                Lead.mailing_address.ilike(term),
            )
        )

    total = db.scalar(select(func.count()).select_from(stmt.subquery())) or 0
    rows = db.scalars(stmt.order_by(Lead.created_at.desc()).offset(offset).limit(limit)).all()
    return LeadListResponse(
        items=[LeadOut.model_validate(row) for row in rows],
        pagination={"total": total, "limit": limit, "offset": offset},
    )


@router.get("/{lead_id}", response_model=LeadOut)
def get_lead(lead_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> LeadOut:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    return LeadOut.model_validate(lead)


@router.patch("/{lead_id}/notes", response_model=LeadOut)
def update_lead_notes(
    lead_id: int,
    payload: LeadUpdateNotes,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadOut:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    lead.notes = payload.notes
    db.add(LeadTimeline(lead_id=lead.id, event_type="lead.notes.updated", payload={"notes": payload.notes}))
    log_audit(
        db,
        event_type="lead.edit",
        entity_type="lead",
        entity_id=str(lead.id),
        actor_user_id=current_user.id,
        actor_label=current_user.email,
        summary="Lead notes updated",
    )
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)


@router.post("/{lead_id}/notes", response_model=LeadNoteResponse)
def add_note(
    lead_id: int,
    payload: LeadNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadNoteResponse:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    note = LeadNote(lead_id=lead.id, note=payload.note, created_by_user_id=current_user.id)
    db.add(note)
    db.add(LeadTimeline(lead_id=lead.id, event_type="lead.note.added", payload={"note": payload.note}))
    log_audit(
        db,
        event_type="lead.note.added",
        entity_type="lead",
        entity_id=str(lead.id),
        actor_user_id=current_user.id,
        actor_label=current_user.email,
        summary="Lead note added",
    )
    db.commit()
    db.refresh(note)
    return LeadNoteResponse.model_validate(note)


@router.get("/{lead_id}/timeline", response_model=LeadTimelineResponse)
def get_timeline(lead_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)) -> LeadTimelineResponse:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    events = db.scalars(select(LeadTimeline).where(LeadTimeline.lead_id == lead.id).order_by(LeadTimeline.created_at.desc())).all()
    return LeadTimelineResponse(items=[LeadTimelineEvent.model_validate(row) for row in events])


@router.post("/{lead_id}/legal-review/clear", response_model=LeadOut)
def clear_legal_review(
    lead_id: int,
    payload: LegalReviewClearRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> LeadOut:
    lead = db.get(Lead, lead_id)
    if not lead:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lead not found")
    lead.legal_review_cleared = payload.legal_review_cleared
    db.add(LeadTimeline(lead_id=lead.id, event_type="lead.legal_review.updated", payload=payload.model_dump()))
    if payload.legal_review_cleared:
        create_notification(db, str(lead.id), "legal_review_required", "Legal review cleared for lead")
    log_audit(
        db,
        event_type="legal_review.clear",
        entity_type="lead",
        entity_id=str(lead.id),
        actor_user_id=current_user.id,
        actor_label=current_user.email,
    )
    db.commit()
    db.refresh(lead)
    return LeadOut.model_validate(lead)

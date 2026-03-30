from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.enums import LetterStatus, LetterTemplateKey, LeadStatus, TrackingStatus
from app.models.lead import Lead, LeadTimeline
from app.models.letter import Letter
from app.models.tracking import TrackingEvent
from app.models.user import User
from app.schemas.letter import LetterDecisionRequest, LetterOut, LetterPreviewRequest, LetterQueueResponse
from app.services.audit import log_audit
from app.services.lob_service import LobService
from app.services.notifications import create_notification

router = APIRouter(prefix="/letters")


@router.get("/queue", response_model=LetterQueueResponse)
def letter_queue(
    status: LetterStatus | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=200),
    offset: int = Query(default=0, ge=0),
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LetterQueueResponse:
    stmt = select(Letter).order_by(Letter.created_at.desc()).offset(offset).limit(limit)
    if status:
        stmt = stmt.where(Letter.status == status.value)
    items = db.scalars(stmt).all()
    total = db.query(Letter).count()
    return LetterQueueResponse(
        items=[LetterOut.model_validate(x) for x in items],
        pagination={"total": total, "limit": limit, "offset": offset},
    )


@router.post("/preview", response_model=LetterOut)
def preview_letter(
    payload: LetterPreviewRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LetterOut:
    lead = db.get(Lead, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")

    if payload.template_key == LetterTemplateKey.FLORIDA_OUTREACH and not lead.legal_review_cleared:
        raise HTTPException(status_code=400, detail="Florida letters require legal review clearance")

    if not lead.mailing_address:
        raise HTTPException(status_code=400, detail="Mailing address required for letter workflow")

    lob = LobService()
    verified, standardized = lob.verify_address(lead.mailing_address)
    body = lob.render_template(payload.template_key.value, lead)
    letter = Letter(
        lead_id=lead.id,
        template_key=payload.template_key.value,
        status=LetterStatus.PENDING_APPROVAL.value,
        body=body,
        preview_payload={"lob_verified": verified, "standardized": standardized},
    )
    db.add(letter)
    db.add(LeadTimeline(lead_id=lead.id, event_type="letter.previewed", payload={"template_key": payload.template_key.value}))
    db.commit()
    db.refresh(letter)
    log_audit(
        db,
        event_type="letter_previewed",
        entity_type="letter",
        entity_id=str(letter.id),
        actor_user_id=user.id,
        actor_label=user.email,
    )
    db.commit()
    return LetterOut.model_validate(letter)


@router.post("/{letter_id}/approve", response_model=LetterOut)
def approve_letter(
    letter_id: int,
    payload: LetterDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LetterOut:
    letter = db.get(Letter, letter_id)
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    lead = db.get(Lead, letter.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    if letter.template_key == LetterTemplateKey.FLORIDA_OUTREACH.value and not lead.legal_review_cleared:
        raise HTTPException(status_code=400, detail="Florida legal review is required")

    lob = LobService()
    lob_id = lob.send_letter(letter)
    letter.status = LetterStatus.SENT.value
    letter.lob_letter_id = lob_id
    lead.status = LeadStatus.MAILED.value
    db.add(
        TrackingEvent(
            lead_id=lead.id,
            letter_id=letter.id,
            status=TrackingStatus.SUBMITTED.value,
            external_id=lob_id,
            details='{"source":"lob","status":"submitted"}',
        )
    )
    db.add(
        LeadTimeline(
            lead_id=lead.id,
            event_type="letter.approved_and_sent",
            payload={"letter_id": letter.id, "note": payload.note},
        )
    )
    create_notification(db, lead.id, "approved_letter_mailed", "Approved letter mailed")
    db.commit()
    db.refresh(letter)
    log_audit(
        db,
        event_type="letter_approved",
        entity_type="letter",
        entity_id=str(letter.id),
        actor_user_id=user.id,
        actor_label=user.email,
        metadata={"note": payload.note, "lob_letter_id": lob_id},
    )
    db.commit()
    return LetterOut.model_validate(letter)


@router.post("/{letter_id}/reject", response_model=LetterOut)
def reject_letter(
    letter_id: int,
    payload: LetterDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LetterOut:
    letter = db.get(Letter, letter_id)
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    letter.status = LetterStatus.REJECTED.value
    letter.rejection_reason = payload.rejection_reason or payload.note
    db.commit()
    db.refresh(letter)
    log_audit(
        db,
        event_type="letter_rejected",
        entity_type="letter",
        entity_id=str(letter.id),
        actor_user_id=user.id,
        actor_label=user.email,
        metadata={"reason": letter.rejection_reason},
    )
    db.commit()
    return LetterOut.model_validate(letter)


@router.post("/{letter_id}/hold", response_model=LetterOut)
def hold_letter(
    letter_id: int,
    payload: LetterDecisionRequest,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> LetterOut:
    letter = db.get(Letter, letter_id)
    if not letter:
        raise HTTPException(status_code=404, detail="Letter not found")
    letter.status = LetterStatus.HOLD.value
    letter.hold_reason = payload.hold_reason or payload.note
    db.commit()
    db.refresh(letter)
    log_audit(
        db,
        event_type="letter_held",
        entity_type="letter",
        entity_id=str(letter.id),
        actor_user_id=user.id,
        actor_label=user.email,
        metadata={"reason": letter.hold_reason},
    )
    db.commit()
    return LetterOut.model_validate(letter)

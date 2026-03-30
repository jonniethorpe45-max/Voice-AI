from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.enums import LeadStatus, NotificationType, ResponseChannel
from app.models.lead import Lead, LeadTimeline
from app.models.response_event import ResponseEvent
from app.schemas.response_event import ResponseEventCreate, ResponseEventOut
from app.services.audit import log_audit
from app.services.notifications import create_notification

router = APIRouter(prefix="/responses")


def _persist_response(db: Session, lead: Lead, channel: ResponseChannel, payload: dict, note: str | None) -> ResponseEvent:
    event = ResponseEvent(
        lead_id=lead.id,
        channel=channel.value,
        payload_json=payload,
        operator_note=note,
    )
    db.add(event)
    lead.status = LeadStatus.RESPONDED.value
    db.add(
        LeadTimeline(
            lead_id=lead.id,
            event_type="response.received",
            payload={"channel": channel.value},
        )
    )
    create_notification(
        db,
        lead_id=lead.id,
        event_type=NotificationType.RECIPIENT_RESPONDED.value,
        message="Recipient responded",
    )
    db.commit()
    db.refresh(event)
    return event


@router.post("/manual", response_model=ResponseEventOut)
def create_manual_response(
    payload: ResponseEventCreate,
    db: Session = Depends(get_db),
    user=Depends(get_current_user),
) -> ResponseEventOut:
    lead = db.get(Lead, payload.lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    event = _persist_response(
        db,
        lead,
        payload.channel,
        payload.payload,
        payload.operator_note or f"logged by {user.email}",
    )
    log_audit(
        db,
        actor_user_id=user.id,
        actor_label=user.email,
        event_type="response.manual.logged",
        entity_type="lead",
        entity_id=str(lead.id),
    )
    db.commit()
    return ResponseEventOut.model_validate(event)


@router.post("/webhooks/email", response_model=ResponseEventOut)
async def inbound_email_webhook(request: Request, db: Session = Depends(get_db)) -> ResponseEventOut:
    payload = await request.json()
    lead_id = payload.get("lead_id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="lead_id is required")
    lead = db.get(Lead, int(lead_id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    event = _persist_response(db, lead, ResponseChannel.EMAIL, payload, note=None)
    return ResponseEventOut.model_validate(event)


@router.post("/webhooks/twilio", response_model=ResponseEventOut)
async def inbound_twilio_webhook(request: Request, db: Session = Depends(get_db)) -> ResponseEventOut:
    form = await request.form()
    lead_id = form.get("lead_id")
    if not lead_id:
        raise HTTPException(status_code=400, detail="lead_id is required")
    lead = db.get(Lead, int(lead_id))
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    payload = {
        "from": form.get("From"),
        "to": form.get("To"),
        "body": form.get("Body"),
    }
    event = _persist_response(db, lead, ResponseChannel.TWILIO, payload, note=None)
    return ResponseEventOut.model_validate(event)


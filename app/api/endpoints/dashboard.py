from decimal import Decimal

from fastapi import APIRouter, Depends
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.enums import LeadStatus
from app.models.lead import Lead
from app.schemas.dashboard import DashboardStatsOut, PerStateCount, PerStateSurplus

router = APIRouter(prefix="/dashboard")


@router.get("/stats", response_model=DashboardStatsOut)
def dashboard_stats(
    db: Session = Depends(get_db),
    _=Depends(get_current_user),
) -> DashboardStatsOut:
    def count_by_status(status: LeadStatus) -> int:
        return db.query(func.count(Lead.id)).filter(Lead.status == status.value).scalar() or 0

    per_state_counts_raw = db.query(Lead.state, func.count(Lead.id)).group_by(Lead.state).all()
    per_state_surplus_raw = db.query(Lead.state, func.coalesce(func.sum(Lead.surplus_amount), 0)).group_by(Lead.state).all()

    return DashboardStatsOut(
        total_leads=db.query(func.count(Lead.id)).scalar() or 0,
        ready_for_review=count_by_status(LeadStatus.READY_FOR_REVIEW),
        pending_approval=count_by_status(LeadStatus.PENDING_APPROVAL),
        mailed=count_by_status(LeadStatus.MAILED),
        delivered=count_by_status(LeadStatus.DELIVERED),
        returned=count_by_status(LeadStatus.RETURNED),
        responded=count_by_status(LeadStatus.RESPONDED),
        per_state_counts=[PerStateCount(state=s, count=c) for s, c in per_state_counts_raw],
        per_state_surplus_totals=[
            PerStateSurplus(state=s, surplus_total=Decimal(total)) for s, total in per_state_surplus_raw
        ],
    )

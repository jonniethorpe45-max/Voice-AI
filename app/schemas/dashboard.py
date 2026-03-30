from decimal import Decimal

from pydantic import BaseModel


class StateCount(BaseModel):
    state: str
    count: int


class StateSurplusTotal(BaseModel):
    state: str
    surplus_total: Decimal


class DashboardStatsResponse(BaseModel):
    total_leads: int
    ready_for_review: int
    pending_approval: int
    mailed: int
    delivered: int
    returned: int
    responded: int
    per_state_counts: list[StateCount]
    per_state_surplus_totals: list[StateSurplusTotal]

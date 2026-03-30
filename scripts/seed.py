from __future__ import annotations

from datetime import date, datetime, timezone, timedelta
from decimal import Decimal
from uuid import uuid4

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import SessionLocal
from app.core.security import hash_password
from app.models.county_config import CountyConfig
from app.models.enums import CountyKey, LeadStatus
from app.models.lead import Lead
from app.models.letter import Letter
from app.models.tracking import TrackingEvent
from app.models.user import User


COUNTIES = [
    ("CA", "Los Angeles", CountyKey.CA_LA, "trustee_sale", True, 0.85, True),
    ("CA", "Orange", CountyKey.CA_ORANGE, "trustee_sale", True, 0.82, True),
    ("CA", "El Dorado", CountyKey.CA_EL_DORADO, "tax_sale", True, 0.76, True),
    ("CA", "Tulare", CountyKey.CA_TULARE, "tax_sale", True, 0.74, True),
    ("FL", "Lee", CountyKey.FL_LEE, "tax_deed", False, 0.2, True),
    ("FL", "Brevard", CountyKey.FL_BREVARD, "tax_deed", False, 0.2, True),
]


def seed(session: Session) -> None:
    admin = session.scalar(select(User).where(User.email == settings.seed_admin_email))
    if not admin:
        admin = User(
            email=settings.seed_admin_email,
            password_hash=hash_password(settings.seed_admin_password),
            full_name="Surplus Admin",
            is_active=True,
            is_superuser=True,
        )
        session.add(admin)
        session.flush()

    for state, county_name, county_key, sale_type, assignment_supported, conf, manual_review in COUNTIES:
        existing = session.scalar(select(CountyConfig).where(CountyConfig.county_key == county_key.value))
        if existing:
            continue
        session.add(
            CountyConfig(
                state=state,
                county_name=county_name,
                county_key=county_key.value,
                sale_type=sale_type,
                source_urls_json=[f"https://example.local/{county_key.value.lower()}"],
                assignment_supported=assignment_supported,
                assignment_confidence=conf,
                manual_review_required=manual_review,
                active_for_ingestion=True,
                active_for_outreach=True,
                notes=f"Seed config for {county_key.value}",
            )
        )
    session.flush()

    if session.scalar(select(Lead.id).limit(1)):
        session.commit()
        return

    sample_leads = [
        ("CA", "Los Angeles", "Maria Gomez", "123 Main St, Los Angeles, CA", "400 Pine Ave, Los Angeles, CA", "LA-123-456", Decimal("13500.00"), LeadStatus.READY_FOR_REVIEW.value, True),
        ("CA", "Orange", "Ana Gomez", "11 Orange Ave, Santa Ana, CA", "11 Orange Ave, Santa Ana, CA", "APN-CAO-2222", Decimal("18600.00"), LeadStatus.PENDING_APPROVAL.value, True),
        ("CA", "El Dorado", "John Doe", "222 Pine St, Placerville, CA 95667", "222 Pine St, Placerville, CA 95667", "244-010-011", Decimal("22000.00"), LeadStatus.MAILED.value, True),
        ("CA", "Tulare", "Devin Ruiz", "22 Palm Ave, Tulare, CA", "78 Olive St, Tulare, CA", "TUL-444", Decimal("15500.00"), LeadStatus.DELIVERED.value, True),
        ("FL", "Lee", "Nora Diaz", "PO Box 11, Fort Myers, FL", "511 Riverside Dr, Fort Myers, FL", "FL-LEE-771", Decimal("8600.00"), LeadStatus.RETURNED.value, True),
        ("FL", "Brevard", "Tyler Nguyen", "PO Box 9181, Melbourne, FL", "545 River Trail, Melbourne, FL", "28-37-05-23-00000.0-0007.00", Decimal("6810.00"), LeadStatus.RESPONDED.value, True),
    ]

    for i, row in enumerate(sample_leads):
        state, county, owner, mailing, property_addr, parcel, amount, status, legal_cleared = row
        lead = Lead(
            state=state,
            county=county,
            owner_name=owner,
            mailing_address=mailing,
            property_address=property_addr,
            parcel_number=parcel,
            sale_date=date(2024, 1, 1) + timedelta(days=i),
            surplus_amount=amount,
            status=status,
            legal_review_cleared=legal_cleared,
            manual_review_required=True,
            assignment_confidence=0.8 if state == "CA" else 0.2,
            source_url=f"https://example.local/{county.lower().replace(' ', '-')}",
            source_hash=f"seed-{uuid4()}",
            notes="Seed lead",
        )
        session.add(lead)
        session.flush()
        if status in {LeadStatus.MAILED.value, LeadStatus.DELIVERED.value, LeadStatus.RETURNED.value, LeadStatus.RESPONDED.value}:
            letter = Letter(
                lead_id=lead.id,
                template_key="california_outreach_letter" if state == "CA" else "florida_outreach_letter",
                status="sent",
                body="Seed letter. You may be able to claim these funds directly without paying a fee.",
                lob_letter_id=f"lob-seed-{lead.id}",
                approved_by_user_id=admin.id,
            )
            session.add(letter)
            session.flush()
            session.add(
                TrackingEvent(
                    lead_id=lead.id,
                    letter_id=letter.id,
                    status=status if status in {"mailed", "delivered", "returned"} else "mailed",
                    external_id=letter.lob_letter_id,
                    details={"seed": True},
                    event_time=datetime.now(timezone.utc),
                )
            )

    session.commit()


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed(db)
        print("Seed complete")
    finally:
        db.close()

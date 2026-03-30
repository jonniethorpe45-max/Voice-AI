from __future__ import annotations

from dataclasses import asdict

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models.county_config import CountyConfig
from app.models.enums import LeadStatus
from app.models.ingestion import ImportRun, RawSourceSnapshot
from app.models.lead import Lead, LeadTimeline
from app.services.contact_enrichment import ContactEnrichmentService
from app.services.ingestion.adapters import get_adapter
from app.services.normalization import normalize_address, normalize_name, quality_and_flags, source_hash


def run_ingestion_for_county(db: Session, county_key: str) -> dict:
    county = db.scalar(select(CountyConfig).where(CountyConfig.county_key == county_key))
    if county is None:
        return {"county_key": county_key, "status": "not_found"}
    if not county.active_for_ingestion:
        return {"county_key": county_key, "status": "inactive"}

    adapter = get_adapter(county_key)
    source_urls = county.source_urls_json or []
    if not source_urls:
        return {"county_key": county_key, "status": "no_sources"}

    run = ImportRun(county_key=county_key, source_url=source_urls[0], status="running")
    db.add(run)
    db.flush()

    inserted = 0
    flagged = 0
    seen = 0
    enrichment = ContactEnrichmentService()

    for src in source_urls:
        records = adapter.fetch_and_parse(src)
        seen += len(records)
        for record in records:
            dedupe_hash = source_hash(record.owner_name, record.property_address, record.county, src)
            if db.scalar(select(Lead).where(Lead.source_hash == dedupe_hash).limit(1)):
                continue

            owner = normalize_name(record.owner_name)
            property_addr = normalize_address(record.property_address or "")
            dup_owner = db.scalar(select(Lead.id).where(Lead.owner_name == owner).limit(1)) is not None
            dup_property = (
                db.scalar(select(Lead.id).where(Lead.property_address == property_addr).limit(1)) is not None
                if property_addr
                else False
            )
            q = quality_and_flags(
                state=record.state,
                county_key=county_key,
                mailing_address=record.mailing_address,
                assignment_confidence=county.assignment_confidence,
                duplicate_owner=dup_owner,
                duplicate_property=dup_property,
            )
            contact = enrichment.enrich(record.mailing_address)
            manual_review = record.manual_review_required or county.manual_review_required
            if not contact.mailing_address_ok:
                manual_review = True

            lead = Lead(
                state=record.state,
                county=record.county,
                owner_name=owner,
                mailing_address=record.mailing_address,
                property_address=property_addr or None,
                parcel_number=record.parcel_number,
                sale_date=record.sale_date,
                surplus_amount=record.surplus_amount,
                status=LeadStatus.NEW.value if manual_review else LeadStatus.READY_FOR_REVIEW.value,
                manual_review_required=manual_review,
                legal_review_cleared=False,
                assignment_confidence=county.assignment_confidence,
                source_url=src,
                source_hash=dedupe_hash,
                quality_score=q.quality_score,
                probate_risk=q.probate_risk,
                duplicate_owner=q.duplicate_owner,
                duplicate_property=q.duplicate_property,
                florida_manual_only=q.florida_manual_only,
                california_assignment_possible=q.california_assignment_possible,
                extraction_metadata={
                    **record.extraction_metadata,
                    "mailing_address_ok": contact.mailing_address_ok,
                },
            )
            db.add(lead)
            db.flush()
            db.add(
                LeadTimeline(
                    lead_id=lead.id,
                    event_type="lead_created",
                    payload={"county_key": county_key, "import_run_id": run.id},
                )
            )
            db.add(
                RawSourceSnapshot(
                    import_run_id=run.id,
                    lead_id=lead.id,
                    source_type="html",
                    source_url=src,
                    content=f"<snapshot county='{county_key}' owner='{owner}'/>",
                    extraction_metadata_json=asdict(record),
                )
            )
            inserted += 1
            if manual_review:
                flagged += 1

    run.records_seen = seen
    run.records_inserted = inserted
    run.records_flagged = flagged
    run.status = "completed"
    db.commit()
    return {"county_key": county_key, "run_id": run.id, "seen": seen, "inserted": inserted, "flagged": flagged}


def run_ingestion_for_active_counties(db: Session) -> dict[str, dict]:
    counties = db.scalars(select(CountyConfig).where(CountyConfig.active_for_ingestion.is_(True))).all()
    results: dict[str, dict] = {}
    for c in counties:
        results[c.county_key] = run_ingestion_for_county(db, c.county_key)
    return results

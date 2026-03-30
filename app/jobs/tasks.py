from sqlalchemy.orm import Session

from app.core.database import SessionLocal
from app.services.ingestion.engine import run_ingestion_for_county


def run_county_ingestion_task(county_key: str) -> dict:
    db: Session = SessionLocal()
    try:
        return run_ingestion_for_county(db, county_key)
    finally:
        db.close()

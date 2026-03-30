from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.api.deps import require_active_user
from app.core.database import get_db
from app.services.ingestion.engine import run_ingestion_for_active_counties

router = APIRouter(prefix="/ingestion")


@router.post("/run")
def run_ingestion(db: Session = Depends(get_db), _=Depends(require_active_user)) -> dict:
    result = run_ingestion_for_active_counties(db)
    return {"message": "ingestion completed", "result": result}

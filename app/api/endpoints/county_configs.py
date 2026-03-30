from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.county_config import CountyConfig
from app.models.enums import CountyKey
from app.models.user import User
from app.schemas.county import CountyConfigCreate, CountyConfigResponse, CountyConfigUpdate
from app.services.audit import log_audit

router = APIRouter(prefix="/county-configs")


@router.get("", response_model=list[CountyConfigResponse])
def list_county_configs(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
) -> list[CountyConfig]:
    return list(db.scalars(select(CountyConfig).order_by(CountyConfig.state, CountyConfig.county_name)))


@router.post("", response_model=CountyConfigResponse, status_code=status.HTTP_201_CREATED)
def create_county_config(
    payload: CountyConfigCreate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CountyConfig:
    if payload.county_key not in [k.value for k in CountyKey]:
        raise HTTPException(status_code=400, detail="Unsupported county key")
    existing = db.scalar(select(CountyConfig).where(CountyConfig.county_key == payload.county_key.value))
    if existing:
        raise HTTPException(status_code=409, detail="County config already exists")
    obj = CountyConfig(**payload.model_dump(mode="json"))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    log_audit(
        db,
        event_type="county_config.created",
        entity_type="county_config",
        entity_id=str(obj.id),
        actor_user_id=user.id,
        actor_label=user.email,
        summary="County config created",
    )
    db.commit()
    return obj


@router.patch("/{county_config_id}", response_model=CountyConfigResponse)
def update_county_config(
    county_config_id: int,
    payload: CountyConfigUpdate,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
) -> CountyConfig:
    obj = db.get(CountyConfig, county_config_id)
    if not obj:
        raise HTTPException(status_code=404, detail="County config not found")
    for key, val in payload.model_dump(exclude_unset=True, mode="json").items():
        setattr(obj, key, val)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    log_audit(
        db,
        event_type="county_config.updated",
        entity_type="county_config",
        entity_id=str(obj.id),
        actor_user_id=user.id,
        actor_label=user.email,
        summary="County config updated",
    )
    db.commit()
    return obj

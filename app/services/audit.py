from __future__ import annotations

from sqlalchemy.orm import Session

from app.models.audit import AuditLog


def add_audit_log(
    db: Session,
    *,
    event_type: str,
    entity_type: str,
    entity_id: str | None,
    summary: str | None = None,
    actor_user_id: int | None = None,
    actor_label: str = "system",
    metadata_json: dict | None = None,
) -> None:
    db.add(
        AuditLog(
            event_type=event_type,
            entity_type=entity_type,
            entity_id=entity_id,
            summary=summary,
            actor_user_id=actor_user_id,
            actor_label=actor_label,
            metadata_json=metadata_json or {},
        )
    )


def log_audit(
    db: Session,
    *,
    event_type: str,
    entity_type: str,
    entity_id: str | None,
    summary: str | None = None,
    actor_user_id: int | None = None,
    actor_label: str = "system",
    metadata: dict | None = None,
) -> None:
    add_audit_log(
        db,
        event_type=event_type,
        entity_type=entity_type,
        entity_id=entity_id,
        summary=summary,
        actor_user_id=actor_user_id,
        actor_label=actor_label,
        metadata_json=metadata or {},
    )

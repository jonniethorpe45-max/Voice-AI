from sqlalchemy.orm import Session

from app.models.notification import Notification


def create_notification(db: Session, lead_id: int | None, event_type: str, message: str) -> Notification:
    row = Notification(lead_id=lead_id, event_type=event_type, message=message)
    db.add(row)
    db.flush()
    return row

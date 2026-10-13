from sqlalchemy.orm import Session

from app.models.audit import AuditLogEntry
from app.models.user import User


def log_action(
    db: Session,
    *,
    actor: User,
    action: str,
    resource_type: str,
    resource_id: str,
    project_id: str | None = None,
    ip_address: str = "127.0.0.1",
) -> AuditLogEntry:
    entry = AuditLogEntry(
        project_id=project_id,
        actor=actor.name,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        ip_address=ip_address,
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

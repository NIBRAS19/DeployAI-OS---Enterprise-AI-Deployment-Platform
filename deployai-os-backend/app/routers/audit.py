from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.audit import AuditLogEntry
from app.models.user import User
from app.schemas.audit import AuditLogEntryOut

router = APIRouter(prefix="/projects/{project_id}/audit", tags=["audit"])


@router.get("", response_model=list[AuditLogEntryOut])
def list_audit_log(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(AuditLogEntry)
        .filter(AuditLogEntry.project_id == project_id)
        .order_by(AuditLogEntry.timestamp.desc())
        .all()
    )

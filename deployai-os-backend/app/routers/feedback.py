from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.feedback import FeedbackEntry
from app.models.user import User
from app.schemas.feedback import FeedbackCreate, FeedbackOut

router = APIRouter(prefix="/projects/{project_id}/feedback", tags=["feedback"])


@router.get("", response_model=list[FeedbackOut])
def list_feedback(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(FeedbackEntry)
        .filter(FeedbackEntry.project_id == project_id)
        .order_by(FeedbackEntry.created_at.desc())
        .all()
    )


@router.post("", response_model=FeedbackOut, status_code=status.HTTP_201_CREATED)
def create_feedback(
    project_id: str,
    payload: FeedbackCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    entry = FeedbackEntry(project_id=project_id, **payload.model_dump())
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return entry

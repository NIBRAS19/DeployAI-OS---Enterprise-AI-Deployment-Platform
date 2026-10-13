from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.architecture import ArchitectureDecision
from app.models.user import User
from app.schemas.architecture import ArchitectureDecisionCreate, ArchitectureDecisionOut

router = APIRouter(prefix="/projects/{project_id}/architecture", tags=["architecture"])


@router.get("", response_model=list[ArchitectureDecisionOut])
def list_decisions(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(ArchitectureDecision).filter(ArchitectureDecision.project_id == project_id).all()


@router.post("", response_model=ArchitectureDecisionOut, status_code=status.HTTP_201_CREATED)
def create_decision(
    project_id: str,
    payload: ArchitectureDecisionCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    decision = ArchitectureDecision(project_id=project_id, **payload.model_dump())
    db.add(decision)
    db.commit()
    db.refresh(decision)
    return decision

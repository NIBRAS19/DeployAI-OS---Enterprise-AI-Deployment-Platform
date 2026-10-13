from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.requirement import Requirement
from app.models.user import User
from app.schemas.requirement import RequirementCreate, RequirementOut

router = APIRouter(prefix="/projects/{project_id}/requirements", tags=["requirements"])


@router.get("", response_model=list[RequirementOut])
def list_requirements(
    project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    return db.query(Requirement).filter(Requirement.project_id == project_id).all()


@router.post("", response_model=RequirementOut, status_code=status.HTTP_201_CREATED)
def create_requirement(
    project_id: str,
    payload: RequirementCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    requirement = Requirement(project_id=project_id, **payload.model_dump())
    db.add(requirement)
    db.commit()
    db.refresh(requirement)
    return requirement

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.deps import get_current_user
from app.database import get_db
from app.models.project import Project
from app.models.user import User
from app.schemas.project import ProjectCreate, ProjectOut

router = APIRouter(prefix="/projects", tags=["projects"])


@router.get("", response_model=list[ProjectOut])
def list_projects(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Project).all()


@router.get("/{project_id}", response_model=ProjectOut)
def get_project(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    project = db.get(Project, project_id)
    if project is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Project not found")
    return project


@router.post("", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
def create_project(
    payload: ProjectCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    slug = payload.name.lower().replace(" ", "-")
    project = Project(
        id=f"proj-{slug}-{uuid.uuid4().hex[:6]}",
        name=payload.name,
        customer_name=payload.customer_name,
        organization_id=current_user.organization_id,
        environment=payload.environment,
    )
    db.add(project)
    db.commit()
    db.refresh(project)
    log_action(
        db,
        actor=current_user,
        action="PROJECT_CREATED",
        resource_type="project",
        resource_id=project.id,
        project_id=project.id,
    )
    return project

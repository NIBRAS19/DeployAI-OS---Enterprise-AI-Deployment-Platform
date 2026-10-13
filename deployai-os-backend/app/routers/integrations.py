from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.integration import Integration
from app.models.user import User
from app.schemas.integration import IntegrationCreate, IntegrationOut

router = APIRouter(prefix="/projects/{project_id}/integrations", tags=["integrations"])


@router.get("", response_model=list[IntegrationOut])
def list_integrations(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Integration).filter(Integration.project_id == project_id).all()


@router.post("", response_model=IntegrationOut, status_code=status.HTTP_201_CREATED)
def create_integration(
    project_id: str,
    payload: IntegrationCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    integration = Integration(project_id=project_id, **payload.model_dump())
    db.add(integration)
    db.commit()
    db.refresh(integration)
    return integration

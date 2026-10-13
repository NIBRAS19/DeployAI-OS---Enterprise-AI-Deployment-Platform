from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.enums import ProjectStatus
from app.models.organization import Organization
from app.models.project import Project
from app.models.user import User
from app.schemas.organization import OrganizationOut

router = APIRouter(prefix="/organizations", tags=["organizations"])


def _to_out(db: Session, org: Organization) -> OrganizationOut:
    active_count = (
        db.query(Project)
        .filter(Project.organization_id == org.id, Project.status == ProjectStatus.active)
        .count()
    )
    return OrganizationOut(id=org.id, name=org.name, industry=org.industry, active_projects=active_count)


@router.get("", response_model=list[OrganizationOut])
def list_organizations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return [_to_out(db, org) for org in db.query(Organization).all()]


@router.get("/{organization_id}", response_model=OrganizationOut)
def get_organization(
    organization_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)
):
    org = db.get(Organization, organization_id)
    if org is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Organization not found")
    return _to_out(db, org)

import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.deps import get_current_user
from app.database import get_db
from app.models.deployment import Deployment
from app.models.enums import DeploymentStatus
from app.models.user import User
from app.schemas.deployment import DeploymentOut

router = APIRouter(prefix="/projects/{project_id}/deployments", tags=["deployments"])


@router.get("", response_model=list[DeploymentOut])
def list_deployments(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(Deployment)
        .filter(Deployment.project_id == project_id)
        .order_by(Deployment.deployed_at.desc())
        .all()
    )


@router.post("/{deployment_id}/rollback", response_model=DeploymentOut, status_code=status.HTTP_201_CREATED)
def rollback(
    project_id: str,
    deployment_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Rollback doesn't mutate history — it appends a new deployment record
    that redeploys a prior version to the same environment, exactly the way
    a real rollback shows up in a deployment log.
    """
    target = db.get(Deployment, deployment_id)
    if target is None or target.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Deployment not found")

    rollback_record = Deployment(
        id=f"dep-{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        version=target.version,
        environment=target.environment,
        status=DeploymentStatus.healthy,
        deployed_by=current_user.name,
        commit=target.commit,
    )
    db.add(rollback_record)
    db.commit()
    db.refresh(rollback_record)

    log_action(
        db,
        actor=current_user,
        action="DEPLOYMENT_ROLLED_BACK",
        resource_type="deployment",
        resource_id=rollback_record.id,
        project_id=project_id,
    )

    return rollback_record

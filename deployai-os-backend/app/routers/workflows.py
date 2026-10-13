import random
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.deps import get_current_user
from app.database import get_db
from app.models.enums import WorkflowRunOutcome, WorkflowStatus
from app.models.user import User
from app.models.workflow import Workflow, WorkflowRun
from app.schemas.workflow import WorkflowOut, WorkflowRunOut

router = APIRouter(prefix="/projects/{project_id}/workflows", tags=["workflows"])


@router.get("", response_model=list[WorkflowOut])
def list_workflows(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Workflow).filter(Workflow.project_id == project_id).all()


@router.get("/{workflow_id}/runs", response_model=list[WorkflowRunOut])
def list_runs(
    project_id: str,
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    return (
        db.query(WorkflowRun)
        .filter(WorkflowRun.workflow_id == workflow_id)
        .order_by(WorkflowRun.ran_at.desc())
        .all()
    )


@router.post("/{workflow_id}/run", response_model=WorkflowRunOut, status_code=status.HTTP_201_CREATED)
def run_workflow(
    project_id: str,
    workflow_id: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Simulated execution — no real workflow engine is wired in yet (see
    README) — weighted by the workflow's own trailing success rate, so a
    reliable workflow stays mostly reliable and a flaky one keeps showing
    occasional failures.
    """
    workflow = db.get(Workflow, workflow_id)
    if workflow is None or workflow.project_id != project_id:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Workflow not found")

    succeeded = random.random() * 100 <= workflow.success_rate
    outcome = WorkflowRunOutcome.success if succeeded else WorkflowRunOutcome.failed
    detail = (
        "Completed all steps successfully."
        if succeeded
        else "Failed during the human-approval step: reviewer did not respond within the timeout window."
    )

    run = WorkflowRun(workflow_id=workflow.id, outcome=outcome, detail=detail)
    db.add(run)

    workflow.last_run = datetime.now(timezone.utc)
    prior_runs = db.query(WorkflowRun).filter(WorkflowRun.workflow_id == workflow.id).count()
    total_runs = prior_runs + 1
    workflow.success_rate = round(
        ((workflow.success_rate * prior_runs) + (100 if succeeded else 0)) / total_runs, 1
    )
    if workflow.status == WorkflowStatus.draft:
        workflow.status = WorkflowStatus.active

    db.commit()
    db.refresh(run)

    log_action(
        db,
        actor=current_user,
        action="WORKFLOW_RUN_SUCCEEDED" if succeeded else "WORKFLOW_RUN_FAILED",
        resource_type="workflow",
        resource_id=workflow.id,
        project_id=project_id,
    )

    return run

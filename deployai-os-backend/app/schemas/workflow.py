from datetime import datetime

from app.models.enums import WorkflowRunOutcome, WorkflowStatus
from app.schemas.base import CamelModel


class WorkflowOut(CamelModel):
    id: str
    name: str
    status: WorkflowStatus
    last_run: datetime | None
    success_rate: float


class WorkflowRunOut(CamelModel):
    id: str
    outcome: WorkflowRunOutcome
    detail: str
    ran_at: datetime

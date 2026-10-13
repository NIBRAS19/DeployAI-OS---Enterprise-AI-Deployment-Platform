import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import WorkflowRunOutcome, WorkflowStatus


class Workflow(Base):
    __tablename__ = "workflows"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"wf-{uuid.uuid4().hex[:8]}")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[WorkflowStatus] = mapped_column(SAEnum(WorkflowStatus), default=WorkflowStatus.draft)
    last_run: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    success_rate: Mapped[float] = mapped_column(Float, default=100.0)

    project: Mapped["Project"] = relationship()
    runs: Mapped[list["WorkflowRun"]] = relationship(back_populates="workflow", cascade="all, delete-orphan")


class WorkflowRun(Base):
    """One simulated execution of a Workflow, appended by POST /workflows/{id}/run."""

    __tablename__ = "workflow_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"run-{uuid.uuid4().hex[:10]}")
    workflow_id: Mapped[str] = mapped_column(ForeignKey("workflows.id"), nullable=False, index=True)
    outcome: Mapped[WorkflowRunOutcome] = mapped_column(SAEnum(WorkflowRunOutcome), nullable=False)
    detail: Mapped[str] = mapped_column(String, nullable=False)
    ran_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    workflow: Mapped["Workflow"] = relationship(back_populates="runs")

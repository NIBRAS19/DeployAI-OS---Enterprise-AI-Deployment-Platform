import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import DeploymentStatus, Environment


class Deployment(Base):
    __tablename__ = "deployments"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"dep-{uuid.uuid4().hex[:8]}")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String, nullable=False)
    environment: Mapped[Environment] = mapped_column(SAEnum(Environment), nullable=False)
    status: Mapped[DeploymentStatus] = mapped_column(SAEnum(DeploymentStatus), default=DeploymentStatus.healthy)
    deployed_by: Mapped[str] = mapped_column(String, nullable=False)
    deployed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )
    commit: Mapped[str] = mapped_column(String, nullable=False)

    project: Mapped["Project"] = relationship()

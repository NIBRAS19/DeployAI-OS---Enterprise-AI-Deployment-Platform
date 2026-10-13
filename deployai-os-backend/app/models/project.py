from sqlalchemy import ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import Environment, LifecycleStage, ProjectStatus


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[str] = mapped_column(String, primary_key=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    customer_name: Mapped[str] = mapped_column(String, nullable=False)
    organization_id: Mapped[str] = mapped_column(ForeignKey("organizations.id"), nullable=False)
    environment: Mapped[Environment] = mapped_column(SAEnum(Environment), default=Environment.development)
    status: Mapped[ProjectStatus] = mapped_column(SAEnum(ProjectStatus), default=ProjectStatus.active)
    current_stage: Mapped[LifecycleStage] = mapped_column(
        SAEnum(LifecycleStage), default=LifecycleStage.discovery
    )

    organization: Mapped["Organization"] = relationship(back_populates="projects")

import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import RequirementPriority, RequirementStatus, RequirementType


class Requirement(Base):
    __tablename__ = "requirements"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"req-{uuid.uuid4().hex[:8]}")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    type: Mapped[RequirementType] = mapped_column(SAEnum(RequirementType), nullable=False)
    priority: Mapped[RequirementPriority] = mapped_column(SAEnum(RequirementPriority), nullable=False)
    status: Mapped[RequirementStatus] = mapped_column(
        SAEnum(RequirementStatus), default=RequirementStatus.draft
    )
    stakeholder: Mapped[str] = mapped_column(String, nullable=False)

    project: Mapped["Project"] = relationship()

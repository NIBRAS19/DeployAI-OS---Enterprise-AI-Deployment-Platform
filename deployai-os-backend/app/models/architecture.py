import uuid

from sqlalchemy import ForeignKey, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ArchitectureStatus


class ArchitectureDecision(Base):
    __tablename__ = "architecture_decisions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"adr-{uuid.uuid4().hex[:8]}")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String, nullable=False)
    context: Mapped[str] = mapped_column(Text, nullable=False)
    decision: Mapped[str] = mapped_column(Text, nullable=False)
    tradeoffs: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[ArchitectureStatus] = mapped_column(
        SAEnum(ArchitectureStatus), default=ArchitectureStatus.proposed
    )

    project: Mapped["Project"] = relationship()

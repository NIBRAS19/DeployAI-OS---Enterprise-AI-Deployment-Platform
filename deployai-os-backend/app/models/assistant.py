import uuid

from sqlalchemy import Float, ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import CitationMode


class Assistant(Base):
    __tablename__ = "assistants"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"asst-{uuid.uuid4().hex[:8]}")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    model: Mapped[str] = mapped_column(String, nullable=False, default="claude-sonnet-4-6")
    temperature: Mapped[float] = mapped_column(Float, default=0.2)
    knowledge_base: Mapped[str] = mapped_column(String, nullable=False)
    citation_mode: Mapped[CitationMode] = mapped_column(SAEnum(CitationMode), default=CitationMode.always)

    project: Mapped["Project"] = relationship()

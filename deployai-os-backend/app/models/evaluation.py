import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, Float, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class EvaluationRun(Base):
    __tablename__ = "evaluation_runs"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"eval-{uuid.uuid4().hex[:8]}")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    version: Mapped[str] = mapped_column(String, nullable=False)
    date: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    correctness: Mapped[float] = mapped_column(Float, nullable=False)
    faithfulness: Mapped[float] = mapped_column(Float, nullable=False)
    citation_accuracy: Mapped[float] = mapped_column(Float, nullable=False)
    avg_latency: Mapped[float] = mapped_column(Float, nullable=False)

    project: Mapped["Project"] = relationship()

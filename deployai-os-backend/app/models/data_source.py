import uuid

from sqlalchemy import ForeignKey, String
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import DataSourceStatus


class DataSource(Base):
    __tablename__ = "data_sources"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"ds-{uuid.uuid4().hex[:8]}")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    name: Mapped[str] = mapped_column(String, nullable=False)
    kind: Mapped[str] = mapped_column(String, nullable=False)
    record_count: Mapped[str] = mapped_column(String, nullable=False)
    status: Mapped[DataSourceStatus] = mapped_column(
        SAEnum(DataSourceStatus), default=DataSourceStatus.disconnected
    )

    project: Mapped["Project"] = relationship()

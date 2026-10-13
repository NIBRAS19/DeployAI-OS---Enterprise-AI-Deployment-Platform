import uuid
from datetime import datetime, timezone

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import DocumentClassification, DocumentStatus


class KnowledgeDocument(Base):
    __tablename__ = "knowledge_documents"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"doc-{uuid.uuid4().hex[:8]}")
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    filename: Mapped[str] = mapped_column(String, nullable=False)
    department: Mapped[str] = mapped_column(String, nullable=False)
    classification: Mapped[DocumentClassification] = mapped_column(
        SAEnum(DocumentClassification), nullable=False, default=DocumentClassification.internal
    )
    status: Mapped[DocumentStatus] = mapped_column(SAEnum(DocumentStatus), default=DocumentStatus.uploaded)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc)
    )

    project: Mapped["Project"] = relationship()
    chunks: Mapped[list["DocumentChunk"]] = relationship(
        back_populates="document", cascade="all, delete-orphan"
    )

    @property
    def chunk_count(self) -> int:
        return len(self.chunks)


class DocumentChunk(Base):
    """One retrievable unit of a KnowledgeDocument.

    ``embedding`` is stored as a JSON-encoded list of floats so the same
    schema works unmodified on SQLite (demo/tests) and Postgres (docker
    compose). See app/services/vector_store.py for how similarity search is
    performed against each backend — swapping the Postgres path over to a
    native ``vector`` column + pgvector's ``<->`` operator for ANN search at
    scale is a drop-in change behind that same interface.

    ``classification`` is denormalized from the parent document so an
    authorization filter can be applied directly in the chunk query, before
    any similarity scoring happens (ADR-003: authorize before retrieval).
    """

    __tablename__ = "document_chunks"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: f"chk-{uuid.uuid4().hex[:10]}")
    document_id: Mapped[str] = mapped_column(ForeignKey("knowledge_documents.id"), nullable=False, index=True)
    project_id: Mapped[str] = mapped_column(ForeignKey("projects.id"), nullable=False, index=True)
    classification: Mapped[DocumentClassification] = mapped_column(SAEnum(DocumentClassification), nullable=False)
    position: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[str] = mapped_column(Text, nullable=False)  # JSON-encoded list[float]

    document: Mapped["KnowledgeDocument"] = relationship(back_populates="chunks")

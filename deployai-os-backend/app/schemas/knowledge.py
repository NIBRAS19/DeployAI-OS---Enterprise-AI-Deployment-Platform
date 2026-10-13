from typing import TYPE_CHECKING

from app.models.enums import DocumentClassification, DocumentStatus
from app.schemas.base import CamelModel

if TYPE_CHECKING:
    from app.services.vector_store import ScoredChunk


class KnowledgeDocumentOut(CamelModel):
    id: str
    filename: str
    department: str
    classification: DocumentClassification
    status: DocumentStatus
    chunks: int


class DocumentUploadResponse(CamelModel):
    document: KnowledgeDocumentOut
    chunks_created: int


class RetrievedChunk(CamelModel):
    chunk_id: str
    document_filename: str
    classification: DocumentClassification
    content: str
    score: float

    @classmethod
    def from_scored(cls, scored: "ScoredChunk") -> "RetrievedChunk":
        chunk = scored.chunk
        return cls(
            chunk_id=chunk.id,
            document_filename=chunk.document.filename if chunk.document else "unknown",
            classification=chunk.classification,
            content=chunk.content,
            score=round(scored.score, 4),
        )


class RetrievalRequest(CamelModel):
    query: str


class RetrievalResult(CamelModel):
    restricted: bool
    message: str | None = None
    chunks: list[RetrievedChunk] = []

from app.models.enums import CitationMode
from app.schemas.base import CamelModel
from app.schemas.knowledge import RetrievedChunk


class AssistantOut(CamelModel):
    id: str
    name: str
    model: str
    temperature: float
    knowledge_base: str
    citation_mode: CitationMode


class ChatRequest(CamelModel):
    message: str


class ChatResponse(CamelModel):
    reply: str
    restricted: bool
    sources: list[RetrievedChunk] = []
    generated_by: str  # "claude" | "mock"

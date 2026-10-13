from app.models.enums import ArchitectureStatus
from app.schemas.base import CamelModel


class ArchitectureDecisionOut(CamelModel):
    id: str
    title: str
    context: str
    decision: str
    tradeoffs: str
    status: ArchitectureStatus


class ArchitectureDecisionCreate(CamelModel):
    title: str
    context: str
    decision: str
    tradeoffs: str
    status: ArchitectureStatus = ArchitectureStatus.proposed

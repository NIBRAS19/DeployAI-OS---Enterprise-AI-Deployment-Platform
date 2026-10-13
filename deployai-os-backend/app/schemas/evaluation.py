from datetime import datetime

from app.schemas.base import CamelModel


class EvaluationRunOut(CamelModel):
    id: str
    version: str
    date: datetime
    correctness: float
    faithfulness: float
    citation_accuracy: float
    avg_latency: float

from datetime import datetime

from app.models.enums import FeedbackSentiment
from app.schemas.base import CamelModel


class FeedbackOut(CamelModel):
    id: str
    question: str
    sentiment: FeedbackSentiment
    reason: str | None
    created_at: datetime


class FeedbackCreate(CamelModel):
    question: str
    sentiment: FeedbackSentiment
    reason: str | None = None

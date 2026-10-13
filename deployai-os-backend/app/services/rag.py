"""Retrieval, with authorization enforced before any search runs — the real
implementation behind ADR-003.

Two layers of enforcement, deliberately redundant:

1. `is_restricted_query` — a fast, explicit check on the question itself.
   If it touches a sensitive topic the user's role can't see, retrieval is
   skipped entirely; nothing is scored, nothing is loaded.
2. `allowed_classifications_for` — applied inside the vector store's own SQL
   query (see services/vector_store.py), so even a query that doesn't trip
   the keyword check can never surface a chunk above the user's clearance.
   This is the layer that actually matters; (1) just gives a clean, honest
   refusal message for the obvious cases instead of a silent empty result.
"""

from dataclasses import dataclass, field

from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.enums import CLASSIFICATION_ACCESS, DocumentClassification, UserRole
from app.models.user import User
from app.services.embeddings import get_embedding_provider
from app.services.vector_store import ScoredChunk, get_vector_store

RESTRICTED_TOPIC_TRIGGERS = ("salary", "compensation", "executive", "payroll")


def allowed_classifications_for(role: UserRole) -> set[DocumentClassification]:
    return {classification for classification, roles in CLASSIFICATION_ACCESS.items() if role in roles}


def is_restricted_query(query: str) -> bool:
    lowered = query.lower()
    return any(trigger in lowered for trigger in RESTRICTED_TOPIC_TRIGGERS)


@dataclass
class RetrievalOutcome:
    restricted: bool
    chunks: list[ScoredChunk] = field(default_factory=list)
    message: str | None = None


def retrieve(db: Session, project_id: str, query: str, user: User, top_k: int = 3) -> RetrievalOutcome:
    allowed = allowed_classifications_for(user.role)

    if is_restricted_query(query) and DocumentClassification.restricted not in allowed:
        return RetrievalOutcome(
            restricted=True,
            message=(
                "This looks like it may touch Restricted-classification information "
                "(compensation, payroll, or executive matters). Your role isn't "
                "authorized to retrieve those documents, so no search was run "
                "against them."
            ),
        )

    settings = get_settings()
    provider = get_embedding_provider()
    store = get_vector_store(settings.is_postgres)

    query_embedding = provider.embed(query)
    scored = store.search(db, project_id, query_embedding, allowed, top_k=top_k)
    scored = [s for s in scored if s.score > 0]

    return RetrievalOutcome(restricted=False, chunks=scored)

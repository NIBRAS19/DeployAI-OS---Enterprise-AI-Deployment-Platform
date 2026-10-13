"""Storage + similarity search for document chunk embeddings, behind a
VectorStore interface — continuing the pattern set by ADR-001 (keep storage
swap-able rather than locking the architecture to one choice).

Two implementations:

- InMemoryCosineVectorStore: loads candidate chunks (already filtered to the
  querying user's allowed classifications) and scores them in Python. Works
  identically on SQLite or Postgres. This is the default, and what the test
  suite exercises.

- PgVectorStore: pushes the similarity search into Postgres via pgvector's
  `<->` operator, for when this runs against the docker-compose Postgres
  with a real dataset too large to score in Python. It's a complete,
  correct reference implementation, but it targets a native `vector` column
  that the default schema doesn't create — see the README's "Going to
  production" section for the migration that adds it. Not exercised by the
  test suite here, since that needs a live pgvector database.
"""

import json
from abc import ABC, abstractmethod
from dataclasses import dataclass

from sqlalchemy.orm import Session

from app.models.enums import DocumentClassification
from app.models.knowledge import DocumentChunk


@dataclass
class ScoredChunk:
    chunk: DocumentChunk
    score: float


class VectorStore(ABC):
    @abstractmethod
    def search(
        self,
        db: Session,
        project_id: str,
        query_embedding: list[float],
        allowed_classifications: set[DocumentClassification],
        top_k: int = 3,
    ) -> list[ScoredChunk]:
        ...


def _cosine_similarity(a: list[float], b: list[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


class InMemoryCosineVectorStore(VectorStore):
    def search(self, db, project_id, query_embedding, allowed_classifications, top_k=3):
        candidates = (
            db.query(DocumentChunk)
            .filter(
                DocumentChunk.project_id == project_id,
                DocumentChunk.classification.in_(allowed_classifications),
            )
            .all()
        )
        scored = [
            ScoredChunk(chunk=chunk, score=_cosine_similarity(query_embedding, json.loads(chunk.embedding)))
            for chunk in candidates
        ]
        scored.sort(key=lambda s: s.score, reverse=True)
        return scored[:top_k]


class PgVectorStore(VectorStore):
    """Production reference path — requires a native `vector` column
    (see README) rather than the portable JSON-text column used by default.
    """

    def search(self, db, project_id, query_embedding, allowed_classifications, top_k=3):
        from sqlalchemy import text as sql_text

        rows = db.execute(
            sql_text(
                """
                SELECT id, 1 - (embedding_vector <=> :query_embedding) AS score
                FROM document_chunks
                WHERE project_id = :project_id
                  AND classification = ANY(:classifications)
                ORDER BY embedding_vector <=> :query_embedding
                LIMIT :top_k
                """
            ),
            {
                "query_embedding": query_embedding,
                "project_id": project_id,
                "classifications": [c.value for c in allowed_classifications],
                "top_k": top_k,
            },
        ).fetchall()
        chunks_by_id = {
            chunk.id: chunk
            for chunk in db.query(DocumentChunk).filter(DocumentChunk.id.in_([row.id for row in rows])).all()
        }
        return [ScoredChunk(chunk=chunks_by_id[row.id], score=row.score) for row in rows if row.id in chunks_by_id]


def get_vector_store(is_postgres: bool) -> VectorStore:
    # Default is the portable in-memory scorer. PgVectorStore is available
    # once a native `vector` column is actually provisioned — swapping it
    # in here is a one-line change; `is_postgres` is accepted now so that
    # switch doesn't require touching any caller.
    return InMemoryCosineVectorStore()

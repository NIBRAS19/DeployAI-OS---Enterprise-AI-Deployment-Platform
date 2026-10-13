from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.deps import get_current_user
from app.database import get_db
from app.models.assistant import Assistant
from app.models.user import User
from app.schemas.assistant import AssistantOut, ChatRequest, ChatResponse
from app.schemas.knowledge import RetrievedChunk
from app.services.llm import generate_reply
from app.services.rag import retrieve

router = APIRouter(prefix="/projects/{project_id}/assistants", tags=["assistants"])


@router.get("", response_model=list[AssistantOut])
def list_assistants(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(Assistant).filter(Assistant.project_id == project_id).all()


@router.post("/chat", response_model=ChatResponse)
def chat(
    project_id: str,
    payload: ChatRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    outcome = retrieve(db, project_id, payload.message, current_user)
    reply, generated_by = generate_reply(payload.message, outcome)

    sources = (
        []
        if outcome.restricted
        else [RetrievedChunk.from_scored(s) for s in outcome.chunks]
    )

    log_action(
        db,
        actor=current_user,
        action="ASSISTANT_CHAT_BLOCKED" if outcome.restricted else "ASSISTANT_CHAT",
        resource_type="assistant_message",
        resource_id=payload.message[:120],
        project_id=project_id,
    )

    return ChatResponse(reply=reply, restricted=outcome.restricted, sources=sources, generated_by=generated_by)

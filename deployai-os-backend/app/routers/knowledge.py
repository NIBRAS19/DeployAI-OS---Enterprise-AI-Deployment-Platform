import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.core.audit import log_action
from app.core.deps import get_current_user
from app.database import get_db
from app.models.enums import DocumentClassification, DocumentStatus
from app.models.knowledge import DocumentChunk, KnowledgeDocument
from app.models.user import User
from app.schemas.knowledge import (
    DocumentUploadResponse,
    KnowledgeDocumentOut,
    RetrievalRequest,
    RetrievalResult,
    RetrievedChunk,
)
from app.services.chunking import chunk_text
from app.services.embeddings import get_embedding_provider
from app.services.rag import retrieve

router = APIRouter(prefix="/projects/{project_id}/knowledge", tags=["knowledge"])


def _doc_to_out(document: KnowledgeDocument) -> KnowledgeDocumentOut:
    return KnowledgeDocumentOut(
        id=document.id,
        filename=document.filename,
        department=document.department,
        classification=document.classification,
        status=document.status,
        chunks=document.chunk_count,
    )


@router.get("", response_model=list[KnowledgeDocumentOut])
def list_documents(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    documents = db.query(KnowledgeDocument).filter(KnowledgeDocument.project_id == project_id).all()
    return [_doc_to_out(d) for d in documents]


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    project_id: str,
    file: UploadFile = File(...),
    department: str = Form(...),
    classification: DocumentClassification = Form(DocumentClassification.internal),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """Reference implementation ingests plain UTF-8 text. Wiring in real PDF/
    DOCX extraction is a drop-in addition ahead of this decode step — it
    doesn't change anything downstream (chunking, embedding, storage)."""
    raw = await file.read()
    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only UTF-8 text files are supported in this reference implementation",
        )

    document = KnowledgeDocument(
        project_id=project_id,
        filename=file.filename or "untitled.txt",
        department=department,
        classification=classification,
        status=DocumentStatus.processing,
    )
    db.add(document)
    db.flush()

    provider = get_embedding_provider()
    pieces = chunk_text(text)
    for position, piece in enumerate(pieces):
        db.add(
            DocumentChunk(
                document_id=document.id,
                project_id=project_id,
                classification=classification,
                position=position,
                content=piece,
                embedding=json.dumps(provider.embed(piece)),
            )
        )

    document.status = DocumentStatus.indexed if pieces else DocumentStatus.processed
    db.commit()
    db.refresh(document)

    log_action(
        db,
        actor=current_user,
        action="DOCUMENT_UPLOADED",
        resource_type="knowledge_document",
        resource_id=document.id,
        project_id=project_id,
    )

    return DocumentUploadResponse(document=_doc_to_out(document), chunks_created=len(pieces))


@router.post("/search", response_model=RetrievalResult)
def search(
    project_id: str,
    payload: RetrievalRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    outcome = retrieve(db, project_id, payload.query, current_user)

    if outcome.restricted:
        log_action(
            db,
            actor=current_user,
            action="RETRIEVAL_BLOCKED_UNAUTHORIZED",
            resource_type="knowledge_query",
            resource_id=payload.query[:120],
            project_id=project_id,
        )
        return RetrievalResult(restricted=True, message=outcome.message, chunks=[])

    return RetrievalResult(
        restricted=False, chunks=[RetrievedChunk.from_scored(s) for s in outcome.chunks]
    )

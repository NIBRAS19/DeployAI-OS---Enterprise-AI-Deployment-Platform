import random
import uuid

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.evaluation import EvaluationRun
from app.models.user import User
from app.schemas.evaluation import EvaluationRunOut

router = APIRouter(prefix="/projects/{project_id}/evaluations", tags=["evaluations"])


@router.get("", response_model=list[EvaluationRunOut])
def list_evaluations(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return (
        db.query(EvaluationRun)
        .filter(EvaluationRun.project_id == project_id)
        .order_by(EvaluationRun.date.asc())
        .all()
    )


@router.post("/run", response_model=EvaluationRunOut, status_code=status.HTTP_201_CREATED)
def run_evaluation(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Simulated eval run: nudges metrics slightly above the latest recorded
    run, capped at a realistic ceiling — mirroring the gradual-improvement
    trend a real prompt/model iteration cycle produces. No real eval harness
    is wired in yet (see README).
    """
    latest = (
        db.query(EvaluationRun)
        .filter(EvaluationRun.project_id == project_id)
        .order_by(EvaluationRun.date.desc())
        .first()
    )

    def _nudge(value: float, ceiling: float) -> float:
        return round(min(value + random.uniform(0.1, 1.2), ceiling), 1)

    if latest:
        correctness = _nudge(latest.correctness, 99.5)
        faithfulness = _nudge(latest.faithfulness, 99.5)
        citation_accuracy = _nudge(latest.citation_accuracy, 99.5)
        avg_latency = round(max(latest.avg_latency - random.uniform(0.0, 0.15), 0.6), 2)
        next_minor = int(latest.version.rsplit(".", 1)[-1]) + 1
        version = f"{latest.version.rsplit('.', 1)[0]}.{next_minor}"
    else:
        correctness, faithfulness, citation_accuracy, avg_latency, version = 85.0, 88.0, 90.0, 2.4, "v1.0"

    run = EvaluationRun(
        id=f"eval-{uuid.uuid4().hex[:8]}",
        project_id=project_id,
        version=version,
        correctness=correctness,
        faithfulness=faithfulness,
        citation_accuracy=citation_accuracy,
        avg_latency=avg_latency,
    )
    db.add(run)
    db.commit()
    db.refresh(run)
    return run

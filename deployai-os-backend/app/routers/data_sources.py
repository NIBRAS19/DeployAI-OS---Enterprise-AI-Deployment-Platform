from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.database import get_db
from app.models.data_source import DataSource
from app.models.user import User
from app.schemas.data_source import DataSourceCreate, DataSourceOut

router = APIRouter(prefix="/projects/{project_id}/data-sources", tags=["data-sources"])


@router.get("", response_model=list[DataSourceOut])
def list_data_sources(project_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    return db.query(DataSource).filter(DataSource.project_id == project_id).all()


@router.post("", response_model=DataSourceOut, status_code=status.HTTP_201_CREATED)
def create_data_source(
    project_id: str,
    payload: DataSourceCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data_source = DataSource(project_id=project_id, **payload.model_dump())
    db.add(data_source)
    db.commit()
    db.refresh(data_source)
    return data_source

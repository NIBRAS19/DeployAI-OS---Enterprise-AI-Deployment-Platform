from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

import app.models  # noqa: F401 - import populates Base.metadata before create_all
from app.config import get_settings
from app.database import Base, engine
from app.routers import (
    architecture,
    assistants,
    audit,
    auth,
    data_sources,
    deployments,
    evaluations,
    feedback,
    integrations,
    knowledge,
    organizations,
    projects,
    requirements,
    workflows,
)

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Convenience for local/demo use so the API works with zero setup beyond
    # `pip install`. A real deployment manages schema via the Alembic
    # migrations in alembic/ instead — see the README.
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="DeployAI OS API",
    description="Reference backend for the DeployAI OS enterprise AI deployment platform.",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["health"])
def health() -> dict:
    return {"status": "ok"}


app.include_router(auth.router)
app.include_router(organizations.router)
app.include_router(projects.router)
app.include_router(requirements.router)
app.include_router(architecture.router)
app.include_router(integrations.router)
app.include_router(data_sources.router)
app.include_router(knowledge.router)
app.include_router(assistants.router)
app.include_router(workflows.router)
app.include_router(deployments.router)
app.include_router(feedback.router)
app.include_router(evaluations.router)
app.include_router(audit.router)

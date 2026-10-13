import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

import app.models  # noqa: F401 - register all mapped classes on Base.metadata
from app.database import Base, get_db
from app.main import app


@pytest.fixture()
def db_session():
    # StaticPool: a plain ":memory:" SQLite db is per-connection, and the
    # engine's default pooling opens a new connection per request, which
    # would silently give each request an empty database. StaticPool pins
    # the engine to a single shared connection so the whole test sees one
    # consistent in-memory database.
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    testing_session_local = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(bind=engine)
    session = testing_session_local()
    try:
        yield session
    finally:
        session.close()


@pytest.fixture()
def client(db_session):
    def _override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = _override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()


@pytest.fixture()
def register(client):
    """Factory fixture: register(email=..., organization=...) -> auth headers.

    The first user to register under a given organization name becomes its
    admin; anyone registering under an existing organization name joins as
    an employee — this is what lets tests exercise both roles.
    """

    def _register(
        name: str = "Test User",
        email: str = "test.user@example.com",
        organization: str = "Test Org",
        password: str = "password123",
    ) -> dict:
        response = client.post(
            "/auth/register",
            json={"name": name, "email": email, "organization": organization, "password": password},
        )
        assert response.status_code == 201, response.text
        token = response.json()["accessToken"]
        return {"Authorization": f"Bearer {token}"}

    return _register

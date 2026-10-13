import uuid

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.deps import get_current_user
from app.core.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.enums import UserRole
from app.models.organization import Organization
from app.models.user import User
from app.schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserOut

router = APIRouter(prefix="/auth", tags=["auth"])

DEMO_USER_EMAIL = "demo.engineer@gulfbridge.example"


def _issue_token(user: User) -> TokenResponse:
    token = create_access_token(subject=user.id, extra_claims={"role": user.role.value})
    return TokenResponse(access_token=token, user=UserOut.model_validate(user))


@router.post("/register", response_model=TokenResponse, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: Session = Depends(get_db)) -> TokenResponse:
    if db.query(User).filter(User.email == payload.email).first():
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="An account with that email already exists"
        )

    org = db.query(Organization).filter(Organization.name.ilike(payload.organization)).first()
    if org is None:
        org = Organization(id=f"org-{uuid.uuid4().hex[:8]}", name=payload.organization, industry="Unspecified")
        db.add(org)
        db.flush()
        role = UserRole.admin
    else:
        role = UserRole.employee

    user = User(
        name=payload.name,
        email=payload.email,
        password_hash=hash_password(payload.password),
        role=role,
        organization_id=org.id,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _issue_token(user)


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if user is None or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")
    return _issue_token(user)


@router.post("/demo", response_model=TokenResponse)
def demo_login(db: Session = Depends(get_db)) -> TokenResponse:
    """Mirrors the frontend's "Continue as Demo Engineer" shortcut: logs into
    a fixed demo account on the seeded organization, creating it on first
    use if the seed script hasn't been run yet.
    """
    user = db.query(User).filter(User.email == DEMO_USER_EMAIL).first()
    if user is None:
        org = db.query(Organization).first()
        if org is None:
            org = Organization(
                id="org-gulfbridge", name="GulfBridge Professional Services", industry="Professional Services"
            )
            db.add(org)
            db.flush()
        user = User(
            name="Demo Engineer",
            email=DEMO_USER_EMAIL,
            password_hash=hash_password(uuid.uuid4().hex),
            role=UserRole.admin,
            organization_id=org.id,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return _issue_token(user)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return UserOut.model_validate(current_user)

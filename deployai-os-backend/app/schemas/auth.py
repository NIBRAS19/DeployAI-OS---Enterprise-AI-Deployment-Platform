from app.models.enums import UserRole
from app.schemas.base import CamelModel


class RegisterRequest(CamelModel):
    name: str
    email: str
    organization: str
    password: str


class LoginRequest(CamelModel):
    email: str
    password: str


class UserOut(CamelModel):
    id: str
    name: str
    email: str
    role: UserRole
    organization_id: str


class TokenResponse(CamelModel):
    access_token: str
    token_type: str = "bearer"
    user: UserOut

from pydantic import BaseModel, EmailStr, Field

from app.schemas.common import Timestamped


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterRequest(BaseModel):
    tenant_name: str = Field(min_length=2, max_length=160)
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=180)
    password: str = Field(min_length=8, max_length=72)


class UserRead(Timestamped):
    tenant_id: str
    email: EmailStr
    full_name: str
    role: str
    is_active: bool


class UserCreate(BaseModel):
    email: EmailStr
    full_name: str = Field(min_length=2, max_length=180)
    password: str = Field(min_length=8, max_length=72)
    role: str = Field(default="user", pattern="^(user|admin)$")
    is_active: bool = True


class UserUpdate(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=180)
    role: str | None = Field(default=None, pattern="^(user|admin)$")
    is_active: bool | None = None

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import CurrentUser, DbSession
from app.core.security import create_access_token, get_password_hash, verify_password
from app.models.tenant import Tenant
from app.models.user import User
from app.schemas.auth import RegisterRequest, Token, UserRead

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterRequest, db: DbSession) -> User:
    existing_email = db.scalar(select(User).where(User.email == payload.email))
    if existing_email:
        raise HTTPException(status_code=409, detail="Email already registered")

    existing_tenant = db.scalar(select(Tenant).where(Tenant.name == payload.tenant_name))
    if existing_tenant:
        raise HTTPException(status_code=409, detail="Tenant name already exists")

    tenant = Tenant(name=payload.tenant_name)
    db.add(tenant)
    db.flush()

    user = User(
        tenant_id=tenant.id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role="admin",
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(db: DbSession, form_data: OAuth2PasswordRequestForm = Depends()) -> Token:
    user = db.scalar(select(User).where(User.email == form_data.username))
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Inactive account")
    token = create_access_token(subject=user.id, extra_claims={"tenant_id": user.tenant_id, "role": user.role})
    return Token(access_token=token)


@router.get("/me", response_model=UserRead)
def read_me(current_user: CurrentUser) -> User:
    return current_user

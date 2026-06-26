from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import AdminUser, DbSession
from app.core.security import get_password_hash
from app.models.user import User
from app.schemas.auth import UserCreate, UserRead, UserUpdate
from app.schemas.common import Page
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=Page[UserRead])
def list_users(
    db: DbSession,
    current_user: AdminUser,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Page[UserRead]:
    query = select(User).where(User.tenant_id == current_user.tenant_id)
    query = apply_sort(query, User, sort_by, sort_order)
    items, total = paginate(db, query, User, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(payload: UserCreate, db: DbSession, current_user: AdminUser) -> User:
    if db.scalar(select(User).where(User.email == payload.email)):
        raise HTTPException(status_code=409, detail="Email already exists")
    user = User(
        tenant_id=current_user.tenant_id,
        email=payload.email,
        full_name=payload.full_name,
        hashed_password=get_password_hash(payload.password),
        role=payload.role,
        is_active=payload.is_active,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.get("/{user_id}", response_model=UserRead)
def get_user(user_id: str, db: DbSession, current_user: AdminUser) -> User:
    user = db.get(User, user_id)
    if not user or user.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@router.patch("/{user_id}", response_model=UserRead)
def update_user(user_id: str, payload: UserUpdate, db: DbSession, current_user: AdminUser) -> User:
    user = get_user(user_id, db, current_user)
    apply_updates(user, payload)
    db.commit()
    db.refresh(user)
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: str, db: DbSession, current_user: AdminUser) -> None:
    user = get_user(user_id, db, current_user)
    if user.id == current_user.id:
        raise HTTPException(status_code=400, detail="Admin cannot delete self")
    db.delete(user)
    db.commit()

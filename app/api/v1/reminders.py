from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.application import Application
from app.models.reminder import Reminder
from app.schemas.common import Page
from app.schemas.reminder import ReminderCreate, ReminderRead, ReminderUpdate
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/reminders", tags=["reminders"])


def _validate_application(db: DbSession, tenant_id: str, application_id: str | None) -> None:
    if application_id:
        application = db.get(Application, application_id)
        if not application or application.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Application not found")


@router.get("", response_model=Page[ReminderRead])
def list_reminders(
    db: DbSession,
    current_user: CurrentUser,
    is_done: bool | None = None,
    application_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "due_at",
    sort_order: str = "asc",
) -> Page[ReminderRead]:
    query = select(Reminder).where(Reminder.tenant_id == current_user.tenant_id)
    if is_done is not None:
        query = query.where(Reminder.is_done == is_done)
    if application_id:
        query = query.where(Reminder.application_id == application_id)
    query = apply_sort(query, Reminder, sort_by, sort_order)
    items, total = paginate(db, query, Reminder, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=ReminderRead, status_code=status.HTTP_201_CREATED)
def create_reminder(payload: ReminderCreate, db: DbSession, current_user: CurrentUser) -> Reminder:
    _validate_application(db, current_user.tenant_id, payload.application_id)
    reminder = Reminder(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(reminder)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.get("/{reminder_id}", response_model=ReminderRead)
def get_reminder(reminder_id: str, db: DbSession, current_user: CurrentUser) -> Reminder:
    reminder = db.get(Reminder, reminder_id)
    if not reminder or reminder.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Reminder not found")
    return reminder


@router.patch("/{reminder_id}", response_model=ReminderRead)
def update_reminder(
    reminder_id: str, payload: ReminderUpdate, db: DbSession, current_user: CurrentUser
) -> Reminder:
    reminder = get_reminder(reminder_id, db, current_user)
    _validate_application(db, current_user.tenant_id, payload.application_id)
    apply_updates(reminder, payload)
    db.commit()
    db.refresh(reminder)
    return reminder


@router.delete("/{reminder_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_reminder(reminder_id: str, db: DbSession, current_user: CurrentUser) -> None:
    reminder = get_reminder(reminder_id, db, current_user)
    db.delete(reminder)
    db.commit()

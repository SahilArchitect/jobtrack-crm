from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.application import Application
from app.models.note import Note
from app.schemas.common import Page
from app.schemas.note import NoteCreate, NoteRead, NoteUpdate
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/notes", tags=["notes"])


def _validate_application(db: DbSession, tenant_id: str, application_id: str | None) -> None:
    if application_id:
        application = db.get(Application, application_id)
        if not application or application.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Application not found")


@router.get("", response_model=Page[NoteRead])
def list_notes(
    db: DbSession,
    current_user: CurrentUser,
    application_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Page[NoteRead]:
    query = select(Note).where(Note.tenant_id == current_user.tenant_id)
    if application_id:
        query = query.where(Note.application_id == application_id)
    query = apply_sort(query, Note, sort_by, sort_order)
    items, total = paginate(db, query, Note, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=NoteRead, status_code=status.HTTP_201_CREATED)
def create_note(payload: NoteCreate, db: DbSession, current_user: CurrentUser) -> Note:
    _validate_application(db, current_user.tenant_id, payload.application_id)
    note = Note(
        tenant_id=current_user.tenant_id,
        created_by_user_id=current_user.id,
        **payload.model_dump(),
    )
    db.add(note)
    db.commit()
    db.refresh(note)
    return note


@router.get("/{note_id}", response_model=NoteRead)
def get_note(note_id: str, db: DbSession, current_user: CurrentUser) -> Note:
    note = db.get(Note, note_id)
    if not note or note.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


@router.patch("/{note_id}", response_model=NoteRead)
def update_note(note_id: str, payload: NoteUpdate, db: DbSession, current_user: CurrentUser) -> Note:
    note = get_note(note_id, db, current_user)
    _validate_application(db, current_user.tenant_id, payload.application_id)
    apply_updates(note, payload)
    db.commit()
    db.refresh(note)
    return note


@router.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_note(note_id: str, db: DbSession, current_user: CurrentUser) -> None:
    note = get_note(note_id, db, current_user)
    db.delete(note)
    db.commit()

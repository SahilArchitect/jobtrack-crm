from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.application import Application
from app.models.interview import InterviewRound
from app.schemas.common import Page
from app.schemas.interview import InterviewRoundCreate, InterviewRoundRead, InterviewRoundUpdate
from app.services.audit import create_audit_log
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/interviews", tags=["interviews"])


def _validate_application(db: DbSession, tenant_id: str, application_id: str | None) -> None:
    if application_id:
        application = db.get(Application, application_id)
        if not application or application.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Application not found")


@router.get("", response_model=Page[InterviewRoundRead])
def list_interviews(
    db: DbSession,
    current_user: CurrentUser,
    application_id: str | None = None,
    status_filter: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "scheduled_at",
    sort_order: str = "asc",
) -> Page[InterviewRoundRead]:
    query = select(InterviewRound).where(InterviewRound.tenant_id == current_user.tenant_id)
    if application_id:
        query = query.where(InterviewRound.application_id == application_id)
    if status_filter:
        query = query.where(InterviewRound.status == status_filter)
    query = apply_sort(query, InterviewRound, sort_by, sort_order)
    items, total = paginate(db, query, InterviewRound, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=InterviewRoundRead, status_code=status.HTTP_201_CREATED)
def create_interview(payload: InterviewRoundCreate, db: DbSession, current_user: CurrentUser) -> InterviewRound:
    _validate_application(db, current_user.tenant_id, payload.application_id)
    interview = InterviewRound(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(interview)
    db.flush()
    create_audit_log(
        db,
        tenant_id=current_user.tenant_id,
        actor_user_id=current_user.id,
        entity_type="interview_round",
        entity_id=interview.id,
        action="created",
        after=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(interview)
    return interview


@router.get("/{interview_id}", response_model=InterviewRoundRead)
def get_interview(interview_id: str, db: DbSession, current_user: CurrentUser) -> InterviewRound:
    interview = db.get(InterviewRound, interview_id)
    if not interview or interview.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Interview not found")
    return interview


@router.patch("/{interview_id}", response_model=InterviewRoundRead)
def update_interview(
    interview_id: str, payload: InterviewRoundUpdate, db: DbSession, current_user: CurrentUser
) -> InterviewRound:
    interview = get_interview(interview_id, db, current_user)
    before = {"status": interview.status, "scheduled_at": str(interview.scheduled_at)}
    changed = apply_updates(interview, payload)
    if changed:
        create_audit_log(
            db,
            tenant_id=current_user.tenant_id,
            actor_user_id=current_user.id,
            entity_type="interview_round",
            entity_id=interview.id,
            action="updated",
            before=before,
            after=payload.model_dump(exclude_unset=True, mode="json"),
        )
    db.commit()
    db.refresh(interview)
    return interview


@router.delete("/{interview_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_interview(interview_id: str, db: DbSession, current_user: CurrentUser) -> None:
    interview = get_interview(interview_id, db, current_user)
    db.delete(interview)
    db.commit()

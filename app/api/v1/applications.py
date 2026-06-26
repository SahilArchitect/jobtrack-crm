import csv
import io

from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, DbSession
from app.models.application import Application
from app.models.company import Company
from app.models.job_posting import JobPosting
from app.schemas.application import ApplicationCreate, ApplicationRead, ApplicationUpdate
from app.schemas.common import Page
from app.services.audit import create_audit_log
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/applications", tags=["applications"])


def _validate_refs(db: DbSession, tenant_id: str, company_id: str | None, job_posting_id: str | None) -> None:
    if company_id:
        company = db.get(Company, company_id)
        if not company or company.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Company not found")
    if job_posting_id:
        job = db.get(JobPosting, job_posting_id)
        if not job or job.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Job posting not found")
        if company_id and job.company_id != company_id:
            raise HTTPException(status_code=400, detail="Job posting does not belong to company")


@router.get("", response_model=Page[ApplicationRead])
def list_applications(
    db: DbSession,
    current_user: CurrentUser,
    q: str | None = None,
    status_filter: str | None = None,
    location: str | None = None,
    company_id: str | None = None,
    priority: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Page[ApplicationRead]:
    query = select(Application).join(Company).outerjoin(JobPosting).where(Application.tenant_id == current_user.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.where(
            or_(Company.name.ilike(like), JobPosting.role_title.ilike(like), Application.notes.ilike(like))
        )
    if status_filter:
        query = query.where(Application.status == status_filter)
    if location:
        query = query.where(or_(Company.location.ilike(f"%{location}%"), JobPosting.location.ilike(f"%{location}%")))
    if company_id:
        query = query.where(Application.company_id == company_id)
    if priority:
        query = query.where(Application.priority == priority)
    query = apply_sort(query, Application, sort_by, sort_order)
    items, total = paginate(db, query, Application, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=ApplicationRead, status_code=status.HTTP_201_CREATED)
def create_application(payload: ApplicationCreate, db: DbSession, current_user: CurrentUser) -> Application:
    _validate_refs(db, current_user.tenant_id, payload.company_id, payload.job_posting_id)
    application = Application(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(application)
    db.flush()
    create_audit_log(
        db,
        tenant_id=current_user.tenant_id,
        actor_user_id=current_user.id,
        entity_type="application",
        entity_id=application.id,
        action="created",
        after=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(application)
    return application


@router.get("/export/csv")
def export_applications_csv(db: DbSession, current_user: CurrentUser) -> StreamingResponse:
    rows = db.execute(
        select(Application, Company, JobPosting)
        .join(Company, Application.company_id == Company.id)
        .outerjoin(JobPosting, Application.job_posting_id == JobPosting.id)
        .where(Application.tenant_id == current_user.tenant_id)
        .order_by(Application.created_at.desc())
    ).all()

    buffer = io.StringIO()
    writer = csv.writer(buffer)
    writer.writerow([
        "application_id",
        "company",
        "role_title",
        "status",
        "priority",
        "resume_version",
        "applied_at",
        "follow_up_at",
        "source",
        "created_at",
    ])
    for application, company, job in rows:
        writer.writerow([
            application.id,
            company.name,
            job.role_title if job else "",
            application.status,
            application.priority,
            application.resume_version or "",
            application.applied_at or "",
            application.follow_up_at or "",
            application.source or "",
            application.created_at,
        ])
    buffer.seek(0)
    headers = {"Content-Disposition": "attachment; filename=applications.csv"}
    return StreamingResponse(iter([buffer.getvalue()]), media_type="text/csv", headers=headers)


@router.get("/{application_id}", response_model=ApplicationRead)
def get_application(application_id: str, db: DbSession, current_user: CurrentUser) -> Application:
    application = db.get(Application, application_id)
    if not application or application.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Application not found")
    return application


@router.patch("/{application_id}", response_model=ApplicationRead)
def update_application(
    application_id: str, payload: ApplicationUpdate, db: DbSession, current_user: CurrentUser
) -> Application:
    application = get_application(application_id, db, current_user)
    _validate_refs(db, current_user.tenant_id, payload.company_id, payload.job_posting_id)
    before = {"status": application.status, "priority": application.priority, "follow_up_at": str(application.follow_up_at)}
    changed = apply_updates(application, payload)
    if changed:
        create_audit_log(
            db,
            tenant_id=current_user.tenant_id,
            actor_user_id=current_user.id,
            entity_type="application",
            entity_id=application.id,
            action="updated",
            before=before,
            after=payload.model_dump(exclude_unset=True, mode="json"),
        )
    db.commit()
    db.refresh(application)
    return application


@router.delete("/{application_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_application(application_id: str, db: DbSession, current_user: CurrentUser) -> None:
    application = get_application(application_id, db, current_user)
    db.delete(application)
    db.commit()

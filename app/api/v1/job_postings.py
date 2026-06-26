from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, DbSession
from app.models.company import Company
from app.models.job_posting import JobPosting
from app.schemas.common import Page
from app.schemas.job_posting import JobPostingCreate, JobPostingRead, JobPostingUpdate
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/job-postings", tags=["job-postings"])


def _validate_company(db: DbSession, tenant_id: str, company_id: str | None) -> None:
    if company_id:
        company = db.get(Company, company_id)
        if not company or company.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Company not found")


@router.get("", response_model=Page[JobPostingRead])
def list_job_postings(
    db: DbSession,
    current_user: CurrentUser,
    q: str | None = None,
    company_id: str | None = None,
    status_filter: str | None = None,
    location: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Page[JobPostingRead]:
    query = select(JobPosting).where(JobPosting.tenant_id == current_user.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.where(or_(JobPosting.role_title.ilike(like), JobPosting.description.ilike(like)))
    if company_id:
        query = query.where(JobPosting.company_id == company_id)
    if status_filter:
        query = query.where(JobPosting.status == status_filter)
    if location:
        query = query.where(JobPosting.location.ilike(f"%{location}%"))
    query = apply_sort(query, JobPosting, sort_by, sort_order)
    items, total = paginate(db, query, JobPosting, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=JobPostingRead, status_code=status.HTTP_201_CREATED)
def create_job_posting(payload: JobPostingCreate, db: DbSession, current_user: CurrentUser) -> JobPosting:
    _validate_company(db, current_user.tenant_id, payload.company_id)
    job = JobPosting(tenant_id=current_user.tenant_id, **payload.model_dump(mode="json"))
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.get("/{job_id}", response_model=JobPostingRead)
def get_job_posting(job_id: str, db: DbSession, current_user: CurrentUser) -> JobPosting:
    job = db.get(JobPosting, job_id)
    if not job or job.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Job posting not found")
    return job


@router.patch("/{job_id}", response_model=JobPostingRead)
def update_job_posting(
    job_id: str, payload: JobPostingUpdate, db: DbSession, current_user: CurrentUser
) -> JobPosting:
    job = get_job_posting(job_id, db, current_user)
    _validate_company(db, current_user.tenant_id, payload.company_id)
    apply_updates(job, payload)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_job_posting(job_id: str, db: DbSession, current_user: CurrentUser) -> None:
    job = get_job_posting(job_id, db, current_user)
    db.delete(job)
    db.commit()

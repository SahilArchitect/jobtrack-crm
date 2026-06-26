from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, DbSession
from app.models.company import Company
from app.schemas.common import Page
from app.schemas.company import CompanyCreate, CompanyRead, CompanyUpdate
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/companies", tags=["companies"])


@router.get("", response_model=Page[CompanyRead])
def list_companies(
    db: DbSession,
    current_user: CurrentUser,
    q: str | None = None,
    location: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Page[CompanyRead]:
    query = select(Company).where(Company.tenant_id == current_user.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.where(or_(Company.name.ilike(like), Company.industry.ilike(like)))
    if location:
        query = query.where(Company.location.ilike(f"%{location}%"))
    query = apply_sort(query, Company, sort_by, sort_order)
    items, total = paginate(db, query, Company, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=CompanyRead, status_code=status.HTTP_201_CREATED)
def create_company(payload: CompanyCreate, db: DbSession, current_user: CurrentUser) -> Company:
    company = Company(tenant_id=current_user.tenant_id, **payload.model_dump(mode="json"))
    db.add(company)
    db.commit()
    db.refresh(company)
    return company


@router.get("/{company_id}", response_model=CompanyRead)
def get_company(company_id: str, db: DbSession, current_user: CurrentUser) -> Company:
    company = db.get(Company, company_id)
    if not company or company.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Company not found")
    return company


@router.patch("/{company_id}", response_model=CompanyRead)
def update_company(
    company_id: str, payload: CompanyUpdate, db: DbSession, current_user: CurrentUser
) -> Company:
    company = get_company(company_id, db, current_user)
    apply_updates(company, payload)
    db.commit()
    db.refresh(company)
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_company(company_id: str, db: DbSession, current_user: CurrentUser) -> None:
    company = get_company(company_id, db, current_user)
    db.delete(company)
    db.commit()

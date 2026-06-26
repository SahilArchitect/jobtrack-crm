from fastapi import APIRouter, HTTPException, status
from sqlalchemy import or_, select

from app.api.deps import CurrentUser, DbSession
from app.models.company import Company
from app.models.contact import Contact
from app.schemas.common import Page
from app.schemas.contact import ContactCreate, ContactRead, ContactUpdate
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/contacts", tags=["contacts"])


def _validate_company(db: DbSession, tenant_id: str, company_id: str | None) -> None:
    if company_id:
        company = db.get(Company, company_id)
        if not company or company.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Company not found")


@router.get("", response_model=Page[ContactRead])
def list_contacts(
    db: DbSession,
    current_user: CurrentUser,
    q: str | None = None,
    company_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Page[ContactRead]:
    query = select(Contact).where(Contact.tenant_id == current_user.tenant_id)
    if q:
        like = f"%{q}%"
        query = query.where(or_(Contact.name.ilike(like), Contact.email.ilike(like), Contact.title.ilike(like)))
    if company_id:
        query = query.where(Contact.company_id == company_id)
    query = apply_sort(query, Contact, sort_by, sort_order)
    items, total = paginate(db, query, Contact, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=ContactRead, status_code=status.HTTP_201_CREATED)
def create_contact(payload: ContactCreate, db: DbSession, current_user: CurrentUser) -> Contact:
    _validate_company(db, current_user.tenant_id, payload.company_id)
    contact = Contact(tenant_id=current_user.tenant_id, **payload.model_dump(mode="json"))
    db.add(contact)
    db.commit()
    db.refresh(contact)
    return contact


@router.get("/{contact_id}", response_model=ContactRead)
def get_contact(contact_id: str, db: DbSession, current_user: CurrentUser) -> Contact:
    contact = db.get(Contact, contact_id)
    if not contact or contact.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Contact not found")
    return contact


@router.patch("/{contact_id}", response_model=ContactRead)
def update_contact(
    contact_id: str, payload: ContactUpdate, db: DbSession, current_user: CurrentUser
) -> Contact:
    contact = get_contact(contact_id, db, current_user)
    _validate_company(db, current_user.tenant_id, payload.company_id)
    apply_updates(contact, payload)
    db.commit()
    db.refresh(contact)
    return contact


@router.delete("/{contact_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_contact(contact_id: str, db: DbSession, current_user: CurrentUser) -> None:
    contact = get_contact(contact_id, db, current_user)
    db.delete(contact)
    db.commit()

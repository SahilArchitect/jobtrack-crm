from fastapi import APIRouter, HTTPException, status
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.application import Application
from app.models.contact import Contact
from app.models.referral import Referral
from app.schemas.common import Page
from app.schemas.referral import ReferralCreate, ReferralRead, ReferralUpdate
from app.services.audit import create_audit_log
from app.utils.query import apply_sort, apply_updates, paginate

router = APIRouter(prefix="/referrals", tags=["referrals"])


def _validate_refs(db: DbSession, tenant_id: str, application_id: str | None, contact_id: str | None) -> None:
    if application_id:
        application = db.get(Application, application_id)
        if not application or application.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Application not found")
    if contact_id:
        contact = db.get(Contact, contact_id)
        if not contact or contact.tenant_id != tenant_id:
            raise HTTPException(status_code=404, detail="Contact not found")


@router.get("", response_model=Page[ReferralRead])
def list_referrals(
    db: DbSession,
    current_user: CurrentUser,
    status_filter: str | None = None,
    application_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Page[ReferralRead]:
    query = select(Referral).where(Referral.tenant_id == current_user.tenant_id)
    if status_filter:
        query = query.where(Referral.status == status_filter)
    if application_id:
        query = query.where(Referral.application_id == application_id)
    query = apply_sort(query, Referral, sort_by, sort_order)
    items, total = paginate(db, query, Referral, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)


@router.post("", response_model=ReferralRead, status_code=status.HTTP_201_CREATED)
def create_referral(payload: ReferralCreate, db: DbSession, current_user: CurrentUser) -> Referral:
    _validate_refs(db, current_user.tenant_id, payload.application_id, payload.contact_id)
    referral = Referral(tenant_id=current_user.tenant_id, **payload.model_dump())
    db.add(referral)
    db.flush()
    create_audit_log(
        db,
        tenant_id=current_user.tenant_id,
        actor_user_id=current_user.id,
        entity_type="referral",
        entity_id=referral.id,
        action="created",
        after=payload.model_dump(mode="json"),
    )
    db.commit()
    db.refresh(referral)
    return referral


@router.get("/{referral_id}", response_model=ReferralRead)
def get_referral(referral_id: str, db: DbSession, current_user: CurrentUser) -> Referral:
    referral = db.get(Referral, referral_id)
    if not referral or referral.tenant_id != current_user.tenant_id:
        raise HTTPException(status_code=404, detail="Referral not found")
    return referral


@router.patch("/{referral_id}", response_model=ReferralRead)
def update_referral(referral_id: str, payload: ReferralUpdate, db: DbSession, current_user: CurrentUser) -> Referral:
    referral = get_referral(referral_id, db, current_user)
    _validate_refs(db, current_user.tenant_id, referral.application_id, payload.contact_id)
    before = {"status": referral.status, "contact_id": referral.contact_id}
    changed = apply_updates(referral, payload)
    if changed:
        create_audit_log(
            db,
            tenant_id=current_user.tenant_id,
            actor_user_id=current_user.id,
            entity_type="referral",
            entity_id=referral.id,
            action="updated",
            before=before,
            after=payload.model_dump(exclude_unset=True, mode="json"),
        )
    db.commit()
    db.refresh(referral)
    return referral


@router.delete("/{referral_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_referral(referral_id: str, db: DbSession, current_user: CurrentUser) -> None:
    referral = get_referral(referral_id, db, current_user)
    db.delete(referral)
    db.commit()

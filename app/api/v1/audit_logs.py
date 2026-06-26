from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.audit_log import AuditLog
from app.schemas.audit_log import AuditLogRead
from app.schemas.common import Page
from app.utils.query import apply_sort, paginate

router = APIRouter(prefix="/audit-logs", tags=["audit-logs"])


@router.get("", response_model=Page[AuditLogRead])
def list_audit_logs(
    db: DbSession,
    current_user: CurrentUser,
    entity_type: str | None = None,
    entity_id: str | None = None,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "created_at",
    sort_order: str = "desc",
) -> Page[AuditLogRead]:
    query = select(AuditLog).where(AuditLog.tenant_id == current_user.tenant_id)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if entity_id:
        query = query.where(AuditLog.entity_id == entity_id)
    query = apply_sort(query, AuditLog, sort_by, sort_order)
    items, total = paginate(db, query, AuditLog, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)

from datetime import date, datetime

from sqlalchemy import Select, asc, desc, func, select
from sqlalchemy.orm import Session

SORTABLE_DEFAULTS = {"created_at", "updated_at", "name", "status", "location", "role_title"}


def apply_sort(query: Select, model: type, sort_by: str, sort_order: str) -> Select:
    if not hasattr(model, sort_by):
        sort_by = "created_at"
    column = getattr(model, sort_by)
    return query.order_by(asc(column) if sort_order == "asc" else desc(column))


def paginate(db: Session, query: Select, model: type, limit: int, offset: int) -> tuple[list, int]:
    count_query = select(func.count()).select_from(query.order_by(None).subquery())
    total = db.scalar(count_query) or 0
    items = db.scalars(query.limit(limit).offset(offset)).all()
    return items, total


def apply_updates(instance: object, payload: object) -> dict[str, object]:
    data = payload.model_dump(exclude_unset=True)
    for key, value in data.items():
        if value is not None and not isinstance(value, (str, int, float, bool, datetime, date, dict, list)):
            value = str(value)
        setattr(instance, key, value)
    return data

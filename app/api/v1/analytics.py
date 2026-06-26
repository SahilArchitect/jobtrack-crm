from fastapi import APIRouter
from sqlalchemy import select

from app.api.deps import CurrentUser, DbSession
from app.models.weekly_summary import WeeklySummary
from app.schemas.analytics import AnalyticsSummary, TaskRead, WeeklySummaryRead
from app.schemas.common import Page
from app.services.analytics import get_analytics_summary
from app.tasks.weekly_summary import generate_weekly_summary
from app.utils.query import apply_sort, paginate

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary", response_model=AnalyticsSummary)
def analytics_summary(db: DbSession, current_user: CurrentUser) -> dict:
    return get_analytics_summary(db, current_user.tenant_id)


@router.post("/weekly-summary", response_model=TaskRead)
def enqueue_weekly_summary(current_user: CurrentUser) -> TaskRead:
    task = generate_weekly_summary.delay(current_user.tenant_id)
    return TaskRead(task_id=task.id, status_url=f"/api/v1/tasks/{task.id}")


@router.get("/weekly-summaries", response_model=Page[WeeklySummaryRead])
def list_weekly_summaries(
    db: DbSession,
    current_user: CurrentUser,
    limit: int = 20,
    offset: int = 0,
    sort_by: str = "week_start",
    sort_order: str = "desc",
) -> Page[WeeklySummaryRead]:
    query = select(WeeklySummary).where(WeeklySummary.tenant_id == current_user.tenant_id)
    query = apply_sort(query, WeeklySummary, sort_by, sort_order)
    items, total = paginate(db, query, WeeklySummary, limit, offset)
    return Page(items=items, total=total, limit=limit, offset=offset)

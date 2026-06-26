from datetime import datetime, timedelta, timezone

from app.db.session import SessionLocal
from app.models.weekly_summary import WeeklySummary
from app.services.analytics import get_analytics_summary
from app.worker.celery_app import celery_app


@celery_app.task(name="generate_weekly_summary")
def generate_weekly_summary(tenant_id: str) -> dict:
    week_start = (datetime.now(timezone.utc).date() - timedelta(days=datetime.now(timezone.utc).weekday()))
    db = SessionLocal()
    try:
        metrics = get_analytics_summary(db, tenant_id)
        summary = WeeklySummary(tenant_id=tenant_id, week_start=week_start, metrics=metrics)
        db.add(summary)
        db.commit()
        db.refresh(summary)
        return {"weekly_summary_id": summary.id, "week_start": str(summary.week_start), "metrics": metrics}
    finally:
        db.close()

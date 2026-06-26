from datetime import date

from pydantic import BaseModel

from app.schemas.common import Timestamped


class AnalyticsSummary(BaseModel):
    applications_by_status: dict[str, int]
    referral_conversion_rate: float
    interviews_per_week: dict[str, int]
    top_companies_by_response_rate: list[dict[str, object]]
    totals: dict[str, int]


class WeeklySummaryRead(Timestamped):
    tenant_id: str
    week_start: date
    metrics: dict


class TaskRead(BaseModel):
    task_id: str
    status_url: str

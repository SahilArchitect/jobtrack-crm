from collections import defaultdict
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models.application import Application
from app.models.company import Company
from app.models.interview import InterviewRound
from app.models.referral import Referral

RESPONSE_STATUSES = {"screening", "interview", "offer", "rejected"}


def get_analytics_summary(db: Session, tenant_id: str) -> dict:
    application_rows = db.execute(
        select(Application.status, func.count(Application.id))
        .where(Application.tenant_id == tenant_id)
        .group_by(Application.status)
    ).all()
    applications_by_status = {status: count for status, count in application_rows}

    total_applications = sum(applications_by_status.values())
    submitted_referrals = db.scalar(
        select(func.count(Referral.id)).where(
            Referral.tenant_id == tenant_id, Referral.status.in_(["accepted", "submitted"])
        )
    ) or 0
    interviews_from_referrals = db.scalar(
        select(func.count(Application.id))
        .join(Referral, Referral.application_id == Application.id)
        .where(
            Application.tenant_id == tenant_id,
            Referral.status.in_(["accepted", "submitted"]),
            Application.status.in_(["screening", "interview", "offer"]),
        )
    ) or 0
    referral_conversion_rate = round(
        (interviews_from_referrals / submitted_referrals) * 100, 2
        if submitted_referrals else 0.0,
        2,
    )

    now = datetime.now(timezone.utc)
    eight_weeks_ago = now - timedelta(weeks=8)
    interview_rows = db.execute(
        select(InterviewRound.scheduled_at, func.count(InterviewRound.id))
        .where(
            InterviewRound.tenant_id == tenant_id,
            InterviewRound.scheduled_at.is_not(None),
            InterviewRound.scheduled_at >= eight_weeks_ago,
        )
        .group_by(InterviewRound.scheduled_at)
    ).all()
    interviews_per_week: dict[str, int] = defaultdict(int)
    for scheduled_at, count in interview_rows:
        week_key = scheduled_at.date().isocalendar()
        interviews_per_week[f"{week_key.year}-W{week_key.week:02d}"] += count

    company_rows = db.execute(
        select(Company.name, Application.status, func.count(Application.id))
        .join(Application, Application.company_id == Company.id)
        .where(Application.tenant_id == tenant_id)
        .group_by(Company.name, Application.status)
    ).all()
    company_stats: dict[str, dict[str, int]] = defaultdict(lambda: {"total": 0, "responses": 0})
    for company_name, status, count in company_rows:
        company_stats[company_name]["total"] += count
        if status in RESPONSE_STATUSES:
            company_stats[company_name]["responses"] += count
    top_companies = sorted(
        (
            {
                "company": company,
                "applications": stats["total"],
                "responses": stats["responses"],
                "response_rate": round((stats["responses"] / stats["total"]) * 100, 2)
                if stats["total"] else 0.0,
            }
            for company, stats in company_stats.items()
        ),
        key=lambda row: (row["response_rate"], row["applications"]),
        reverse=True,
    )[:5]

    total_interviews = db.scalar(
        select(func.count(InterviewRound.id)).where(InterviewRound.tenant_id == tenant_id)
    ) or 0
    total_referrals = db.scalar(select(func.count(Referral.id)).where(Referral.tenant_id == tenant_id)) or 0

    return {
        "applications_by_status": applications_by_status,
        "referral_conversion_rate": referral_conversion_rate,
        "interviews_per_week": dict(interviews_per_week),
        "top_companies_by_response_rate": top_companies,
        "totals": {
            "applications": total_applications,
            "referrals": total_referrals,
            "interviews": total_interviews,
        },
    }

from fastapi import APIRouter

from app.api.v1 import (
    analytics,
    applications,
    audit_logs,
    auth,
    companies,
    contacts,
    health,
    interviews,
    job_postings,
    notes,
    referrals,
    reminders,
    tasks,
    users,
)

api_router = APIRouter()
api_router.include_router(health.router)
api_router.include_router(auth.router)
api_router.include_router(users.router)
api_router.include_router(companies.router)
api_router.include_router(contacts.router)
api_router.include_router(job_postings.router)
api_router.include_router(applications.router)
api_router.include_router(referrals.router)
api_router.include_router(interviews.router)
api_router.include_router(notes.router)
api_router.include_router(reminders.router)
api_router.include_router(audit_logs.router)
api_router.include_router(analytics.router)
api_router.include_router(tasks.router)

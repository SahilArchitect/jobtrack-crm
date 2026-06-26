from datetime import datetime, timedelta, timezone

from sqlalchemy import select

from app.core.security import get_password_hash
from app.db.session import SessionLocal
from app.models.application import Application
from app.models.company import Company
from app.models.contact import Contact
from app.models.interview import InterviewRound
from app.models.job_posting import JobPosting
from app.models.referral import Referral
from app.models.tenant import Tenant
from app.models.user import User

TENANT_NAME = "Sahil Job Hunt"
ADMIN_EMAIL = "sahil@example.com"
ADMIN_PASSWORD = "Password123!"


def run() -> None:
    db = SessionLocal()
    try:
        existing = db.scalar(select(User).where(User.email == ADMIN_EMAIL))
        if existing:
            print("Seed data already exists.")
            print(f"Login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
            return

        tenant = Tenant(name=TENANT_NAME)
        db.add(tenant)
        db.flush()

        user = User(
            tenant_id=tenant.id,
            email=ADMIN_EMAIL,
            full_name="Sahil Bhatti",
            hashed_password=get_password_hash(ADMIN_PASSWORD),
            role="admin",
        )
        db.add(user)
        db.flush()

        companies = [
            Company(tenant_id=tenant.id, name="Qualcomm", location="Hyderabad", industry="Semiconductors"),
            Company(tenant_id=tenant.id, name="Samsung R&D", location="Bangalore", industry="Product Engineering"),
            Company(tenant_id=tenant.id, name="Tredence", location="Bangalore", industry="Data/AI Consulting"),
        ]
        db.add_all(companies)
        db.flush()

        jobs = [
            JobPosting(
                tenant_id=tenant.id,
                company_id=companies[0].id,
                role_title="Automation Engineer",
                external_job_id="3091673",
                source="Referral",
                location="Bangalore",
                salary_min_lpa=18,
                salary_max_lpa=30,
                description="Python automation, system testing, backend tools.",
            ),
            JobPosting(
                tenant_id=tenant.id,
                company_id=companies[2].id,
                role_title="Back End Engineer",
                external_job_id="879008",
                source="Referral",
                location="Bangalore",
                salary_min_lpa=15,
                salary_max_lpa=28,
                description="FastAPI, PostgreSQL, APIs, backend services.",
            ),
        ]
        db.add_all(jobs)
        db.flush()

        contact = Contact(
            tenant_id=tenant.id,
            company_id=companies[0].id,
            name="Referral Contact",
            email="referrer@example.com",
            title="Software Engineer",
            notes="Demo referrer for API testing.",
        )
        db.add(contact)
        db.flush()

        app1 = Application(
            tenant_id=tenant.id,
            company_id=companies[0].id,
            job_posting_id=jobs[0].id,
            resume_version="R2-System-Test",
            status="interview",
            priority="urgent",
            applied_at=datetime.now(timezone.utc) - timedelta(days=3),
            source="referral",
            notes="High-priority referred application.",
        )
        app2 = Application(
            tenant_id=tenant.id,
            company_id=companies[2].id,
            job_posting_id=jobs[1].id,
            resume_version="R1-Python-Backend",
            status="applied",
            priority="high",
            applied_at=datetime.now(timezone.utc) - timedelta(days=1),
            source="referral",
        )
        db.add_all([app1, app2])
        db.flush()

        referral = Referral(
            tenant_id=tenant.id,
            application_id=app1.id,
            contact_id=contact.id,
            status="submitted",
            requested_at=datetime.now(timezone.utc) - timedelta(days=4),
            referred_at=datetime.now(timezone.utc) - timedelta(days=3),
        )
        interview = InterviewRound(
            tenant_id=tenant.id,
            application_id=app1.id,
            round_number=1,
            round_type="technical",
            scheduled_at=datetime.now(timezone.utc) + timedelta(days=2),
            status="scheduled",
        )
        db.add_all([referral, interview])
        db.commit()

        print("Seed data created.")
        print(f"Login: {ADMIN_EMAIL} / {ADMIN_PASSWORD}")
    finally:
        db.close()


if __name__ == "__main__":
    run()

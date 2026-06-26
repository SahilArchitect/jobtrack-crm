from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class Application(IDMixin, TimestampMixin, Base):
    __tablename__ = "applications"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    job_posting_id: Mapped[str | None] = mapped_column(ForeignKey("job_postings.id", ondelete="SET NULL"), index=True)
    resume_version: Mapped[str | None] = mapped_column(String(120))
    status: Mapped[str] = mapped_column(String(50), default="saved", index=True)
    priority: Mapped[str] = mapped_column(String(30), default="medium", index=True)
    applied_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    follow_up_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    source: Mapped[str | None] = mapped_column(String(120), index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    company = relationship("Company", back_populates="applications")
    job_posting = relationship("JobPosting", back_populates="applications")
    referral = relationship("Referral", back_populates="application", uselist=False)
    interview_rounds = relationship("InterviewRound", back_populates="application", cascade="all, delete-orphan")
    notes_items = relationship("Note", back_populates="application", cascade="all, delete-orphan")
    reminders = relationship("Reminder", back_populates="application", cascade="all, delete-orphan")

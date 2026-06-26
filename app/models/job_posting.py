from sqlalchemy import ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class JobPosting(IDMixin, TimestampMixin, Base):
    __tablename__ = "job_postings"
    __table_args__ = (UniqueConstraint("tenant_id", "external_job_id", name="uq_job_external_id"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    company_id: Mapped[str] = mapped_column(ForeignKey("companies.id", ondelete="CASCADE"), index=True)
    role_title: Mapped[str] = mapped_column(String(220), nullable=False, index=True)
    external_job_id: Mapped[str | None] = mapped_column(String(120), index=True)
    source: Mapped[str | None] = mapped_column(String(120), index=True)
    source_url: Mapped[str | None] = mapped_column(String(900))
    location: Mapped[str | None] = mapped_column(String(180), index=True)
    salary_min_lpa: Mapped[int | None] = mapped_column(Integer)
    salary_max_lpa: Mapped[int | None] = mapped_column(Integer)
    status: Mapped[str] = mapped_column(String(50), default="open", index=True)
    description: Mapped[str | None] = mapped_column(Text)

    company = relationship("Company", back_populates="job_postings")
    applications = relationship("Application", back_populates="job_posting")

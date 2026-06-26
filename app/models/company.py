from sqlalchemy import ForeignKey, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class Company(IDMixin, TimestampMixin, Base):
    __tablename__ = "companies"
    __table_args__ = (UniqueConstraint("tenant_id", "name", name="uq_company_tenant_name"),)

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    name: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    website: Mapped[str | None] = mapped_column(String(500))
    location: Mapped[str | None] = mapped_column(String(180), index=True)
    industry: Mapped[str | None] = mapped_column(String(120))
    notes: Mapped[str | None] = mapped_column(Text)

    contacts = relationship("Contact", back_populates="company", cascade="all, delete-orphan")
    job_postings = relationship("JobPosting", back_populates="company", cascade="all, delete-orphan")
    applications = relationship("Application", back_populates="company")

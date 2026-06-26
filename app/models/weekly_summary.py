from datetime import date

from sqlalchemy import Date, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, IDMixin, TimestampMixin


class WeeklySummary(IDMixin, TimestampMixin, Base):
    __tablename__ = "weekly_summaries"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    week_start: Mapped[date] = mapped_column(Date, index=True)
    metrics: Mapped[dict] = mapped_column(JSON, nullable=False)

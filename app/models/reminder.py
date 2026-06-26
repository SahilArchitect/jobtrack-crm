from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class Reminder(IDMixin, TimestampMixin, Base):
    __tablename__ = "reminders"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    application_id: Mapped[str | None] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    title: Mapped[str] = mapped_column(String(180), nullable=False)
    due_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    is_done: Mapped[bool] = mapped_column(Boolean, default=False, index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    application = relationship("Application", back_populates="reminders")

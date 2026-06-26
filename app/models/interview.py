from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class InterviewRound(IDMixin, TimestampMixin, Base):
    __tablename__ = "interview_rounds"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    round_number: Mapped[int] = mapped_column(Integer, default=1)
    round_type: Mapped[str] = mapped_column(String(80), default="technical", index=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    status: Mapped[str] = mapped_column(String(50), default="scheduled", index=True)
    feedback: Mapped[str | None] = mapped_column(Text)

    application = relationship("Application", back_populates="interview_rounds")

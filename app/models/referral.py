from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, IDMixin, TimestampMixin


class Referral(IDMixin, TimestampMixin, Base):
    __tablename__ = "referrals"

    tenant_id: Mapped[str] = mapped_column(ForeignKey("tenants.id", ondelete="CASCADE"), index=True)
    application_id: Mapped[str] = mapped_column(ForeignKey("applications.id", ondelete="CASCADE"), index=True)
    contact_id: Mapped[str | None] = mapped_column(ForeignKey("contacts.id", ondelete="SET NULL"), index=True)
    status: Mapped[str] = mapped_column(String(50), default="requested", index=True)
    requested_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    referred_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), index=True)
    notes: Mapped[str | None] = mapped_column(Text)

    application = relationship("Application", back_populates="referral")
    contact = relationship("Contact", back_populates="referrals")

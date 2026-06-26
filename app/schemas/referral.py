from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class ReferralBase(BaseModel):
    application_id: str
    contact_id: str | None = None
    status: str = Field(default="requested", pattern="^(requested|accepted|submitted|declined|no_response)$")
    requested_at: datetime | None = None
    referred_at: datetime | None = None
    notes: str | None = None


class ReferralCreate(ReferralBase):
    pass


class ReferralUpdate(BaseModel):
    contact_id: str | None = None
    status: str | None = Field(default=None, pattern="^(requested|accepted|submitted|declined|no_response)$")
    requested_at: datetime | None = None
    referred_at: datetime | None = None
    notes: str | None = None


class ReferralRead(Timestamped, ReferralBase):
    tenant_id: str

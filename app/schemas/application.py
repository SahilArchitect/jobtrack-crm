from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped

APPLICATION_STATUS_PATTERN = "^(saved|applied|referral_requested|referred|screening|interview|offer|rejected|withdrawn)$"
PRIORITY_PATTERN = "^(low|medium|high|urgent)$"


class ApplicationBase(BaseModel):
    company_id: str
    job_posting_id: str | None = None
    resume_version: str | None = Field(default=None, max_length=120)
    status: str = Field(default="saved", pattern=APPLICATION_STATUS_PATTERN)
    priority: str = Field(default="medium", pattern=PRIORITY_PATTERN)
    applied_at: datetime | None = None
    follow_up_at: datetime | None = None
    source: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class ApplicationCreate(ApplicationBase):
    pass


class ApplicationUpdate(BaseModel):
    company_id: str | None = None
    job_posting_id: str | None = None
    resume_version: str | None = Field(default=None, max_length=120)
    status: str | None = Field(default=None, pattern=APPLICATION_STATUS_PATTERN)
    priority: str | None = Field(default=None, pattern=PRIORITY_PATTERN)
    applied_at: datetime | None = None
    follow_up_at: datetime | None = None
    source: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class ApplicationRead(Timestamped, ApplicationBase):
    tenant_id: str

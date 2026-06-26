from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class InterviewRoundBase(BaseModel):
    application_id: str
    round_number: int = Field(default=1, ge=1, le=10)
    round_type: str = Field(default="technical", max_length=80)
    scheduled_at: datetime | None = None
    status: str = Field(default="scheduled", pattern="^(scheduled|completed|cancelled|rescheduled|passed|failed)$")
    feedback: str | None = None


class InterviewRoundCreate(InterviewRoundBase):
    pass


class InterviewRoundUpdate(BaseModel):
    round_number: int | None = Field(default=None, ge=1, le=10)
    round_type: str | None = Field(default=None, max_length=80)
    scheduled_at: datetime | None = None
    status: str | None = Field(default=None, pattern="^(scheduled|completed|cancelled|rescheduled|passed|failed)$")
    feedback: str | None = None


class InterviewRoundRead(Timestamped, InterviewRoundBase):
    tenant_id: str

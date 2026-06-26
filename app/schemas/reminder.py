from datetime import datetime

from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class ReminderBase(BaseModel):
    application_id: str | None = None
    title: str = Field(min_length=1, max_length=180)
    due_at: datetime
    is_done: bool = False
    notes: str | None = None


class ReminderCreate(ReminderBase):
    pass


class ReminderUpdate(BaseModel):
    application_id: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=180)
    due_at: datetime | None = None
    is_done: bool | None = None
    notes: str | None = None


class ReminderRead(Timestamped, ReminderBase):
    tenant_id: str

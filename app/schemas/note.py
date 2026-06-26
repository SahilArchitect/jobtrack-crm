from pydantic import BaseModel, Field

from app.schemas.common import Timestamped


class NoteBase(BaseModel):
    application_id: str | None = None
    title: str = Field(min_length=1, max_length=180)
    body: str = Field(min_length=1)


class NoteCreate(NoteBase):
    pass


class NoteUpdate(BaseModel):
    application_id: str | None = None
    title: str | None = Field(default=None, min_length=1, max_length=180)
    body: str | None = Field(default=None, min_length=1)


class NoteRead(Timestamped, NoteBase):
    tenant_id: str
    created_by_user_id: str

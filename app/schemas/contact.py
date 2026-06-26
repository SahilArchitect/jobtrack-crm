from pydantic import BaseModel, EmailStr, Field, HttpUrl

from app.schemas.common import Timestamped


class ContactBase(BaseModel):
    company_id: str | None = None
    name: str = Field(min_length=1, max_length=180)
    email: EmailStr | None = None
    linkedin_url: HttpUrl | None = None
    title: str | None = Field(default=None, max_length=180)
    notes: str | None = None


class ContactCreate(ContactBase):
    pass


class ContactUpdate(BaseModel):
    company_id: str | None = None
    name: str | None = Field(default=None, min_length=1, max_length=180)
    email: EmailStr | None = None
    linkedin_url: HttpUrl | None = None
    title: str | None = Field(default=None, max_length=180)
    notes: str | None = None


class ContactRead(Timestamped, ContactBase):
    tenant_id: str

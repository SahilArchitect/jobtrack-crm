from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import Timestamped


class CompanyBase(BaseModel):
    name: str = Field(min_length=1, max_length=180)
    website: HttpUrl | None = None
    location: str | None = Field(default=None, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=1, max_length=180)
    website: HttpUrl | None = None
    location: str | None = Field(default=None, max_length=180)
    industry: str | None = Field(default=None, max_length=120)
    notes: str | None = None


class CompanyRead(Timestamped, CompanyBase):
    tenant_id: str

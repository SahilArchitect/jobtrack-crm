from pydantic import BaseModel, Field, HttpUrl

from app.schemas.common import Timestamped


class JobPostingBase(BaseModel):
    company_id: str
    role_title: str = Field(min_length=2, max_length=220)
    external_job_id: str | None = Field(default=None, max_length=120)
    source: str | None = Field(default=None, max_length=120)
    source_url: HttpUrl | None = None
    location: str | None = Field(default=None, max_length=180)
    salary_min_lpa: int | None = Field(default=None, ge=0, le=500)
    salary_max_lpa: int | None = Field(default=None, ge=0, le=500)
    status: str = Field(default="open", pattern="^(open|closed|paused|archived)$")
    description: str | None = None


class JobPostingCreate(JobPostingBase):
    pass


class JobPostingUpdate(BaseModel):
    company_id: str | None = None
    role_title: str | None = Field(default=None, min_length=2, max_length=220)
    external_job_id: str | None = Field(default=None, max_length=120)
    source: str | None = Field(default=None, max_length=120)
    source_url: HttpUrl | None = None
    location: str | None = Field(default=None, max_length=180)
    salary_min_lpa: int | None = Field(default=None, ge=0, le=500)
    salary_max_lpa: int | None = Field(default=None, ge=0, le=500)
    status: str | None = Field(default=None, pattern="^(open|closed|paused|archived)$")
    description: str | None = None


class JobPostingRead(Timestamped, JobPostingBase):
    tenant_id: str

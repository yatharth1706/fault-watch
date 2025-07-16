from datetime import datetime
from pydantic import BaseModel, Field


class ProjectBase(BaseModel):
    """Base project schema"""
    name: str = Field(..., min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    platform: str | None = Field(None, max_length=50)
    retention_days: int | None = Field(None, ge=1, le=365, description="Number of days to retain errors")


class ProjectCreate(ProjectBase):
    """Schema for creating a project"""
    pass


class ProjectUpdate(BaseModel):
    """Schema for updating a project"""
    name: str | None = Field(None, min_length=1, max_length=255)
    slug: str | None = Field(None, min_length=1, max_length=255, pattern="^[a-z0-9-]+$")
    platform: str | None = Field(None, max_length=50)
    retention_days: int | None = Field(None, ge=1, le=365)
    is_active: bool | None = None


class ProjectOut(ProjectBase):
    """Schema for project output"""
    id: int
    organization_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True 
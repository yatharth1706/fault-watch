from datetime import datetime
from pydantic import BaseModel, Field


class APIKeyCreate(BaseModel):
    """Schema for creating an API key"""
    name: str = Field(..., min_length=1, max_length=255)


class APIKeyOut(BaseModel):
    """Schema for API key output (without sensitive data)"""
    id: int
    name: str
    prefix: str
    is_active: bool
    created_at: datetime
    last_used_at: datetime | None = None
    expires_at: datetime | None = None

    class Config:
        from_attributes = True


class APIKeyWithSecret(APIKeyOut):
    """Schema for API key output including the secret (only used once at creation)"""
    key: str 
from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional
from enum import Enum


class GroupStatus(str, Enum):
    UNRESOLVED = "unresolved"
    RESOLVED = "resolved"
    IGNORED = "ignored"


class GroupBase(BaseModel):
    # Core identification
    id: int
    fingerprint: str
    
    # Project and environment
    service: str
    environment: str = "production"
    
    # Error details
    title: str = Field(..., description="Human-readable error title")
    culprit: Optional[str] = Field(None, description="Where the error occurred")
    level: str = "error"
    
    # Status and tracking
    status: GroupStatus = GroupStatus.UNRESOLVED
    first_seen: datetime
    last_seen: datetime
    occurrences: int
    
    # User impact
    users_affected: int = 0
    
    # Legacy field for backward compatibility
    example_message: str


class GroupOut(GroupBase):
    """Used for listing groups"""


class GroupDetailOut(GroupBase):
    """Same fields plus recent raw events"""
    recent_events: Optional[List[dict]] = None


class GroupStatusUpdate(BaseModel):
    """Schema for updating group status"""
    status: GroupStatus


class GroupStats(BaseModel):
    """Schema for group statistics"""
    total_groups: int
    unresolved_groups: int
    resolved_groups: int

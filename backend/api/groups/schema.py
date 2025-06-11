from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class GroupBase(BaseModel):
    fingerprint: str
    service: str
    example_message: str
    first_seen: datetime
    last_seen: datetime
    occurrences: int

class GroupOut(GroupBase):
    """Used for listing groups"""

class GroupDetailOut(GroupBase):
    """Same fields plus recent raw events"""
    recent_events: Optional[List[dict]] = None

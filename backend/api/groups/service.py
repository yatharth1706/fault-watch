from datetime import datetime
from typing import Optional, List
from db.repositories.groups import GroupRepository
from db.models.groups import GroupStatus
from api.groups.schema import GroupOut, GroupDetailOut
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

class GroupService:
    def __init__(self, session: AsyncSession):
        self.repo = GroupRepository(session=session)

    async def list_groups(
        self, 
        service: Optional[str] = None, 
        environment: Optional[str] = None,
        status: Optional[str] = None,
        since: Optional[str] = None, 
        until: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[GroupOut]:
        """List error groups with enhanced filtering"""
        
        # Parse datetime strings
        since_dt = None
        until_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid since date format")
        if until:
            try:
                until_dt = datetime.fromisoformat(until.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid until date format")
        
        # Parse status
        status_enum = None
        if status:
            try:
                status_enum = GroupStatus(status)
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid status")
        
        groups = await self.repo.list(
            service=service,
            environment=environment,
            status=status_enum,
            since=since_dt,
            until=until_dt,
            limit=limit,
            offset=offset
        )
        return [GroupOut(**g.model_dump()) for g in groups]

    async def get_group(self, fingerprint: str) -> GroupDetailOut:
        """Get error group by fingerprint"""
        group = await self.repo.get_by_fingerprint(fingerprint)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # For MVP, we'll leave recent_events empty
        # In a full implementation, you'd fetch recent errors for this group
        return GroupDetailOut(**group.model_dump())
    
    async def update_group_status(self, fingerprint: str, status: str) -> GroupOut:
        """Update the status of an error group"""
        group = await self.repo.get_by_fingerprint(fingerprint)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        try:
            status_enum = GroupStatus(status)
        except ValueError:
            raise HTTPException(status_code=400, detail="Invalid status")
        
        updated_group = await self.repo.update_status(group.id, status_enum)
        return GroupOut(**updated_group.model_dump())
    
    async def get_group_stats(
        self,
        service: Optional[str] = None,
        environment: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None
    ):
        """Get error group statistics"""
        
        # Parse datetime strings
        since_dt = None
        until_dt = None
        if since:
            try:
                since_dt = datetime.fromisoformat(since.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid since date format")
        if until:
            try:
                until_dt = datetime.fromisoformat(until.replace('Z', '+00:00'))
            except ValueError:
                raise HTTPException(status_code=400, detail="Invalid until date format")
        
        return await self.repo.get_stats(
            service=service,
            environment=environment,
            since=since_dt,
            until=until_dt
        )

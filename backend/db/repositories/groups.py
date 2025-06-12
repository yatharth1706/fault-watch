from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_, desc
from db.models.groups import ErrorGroup, GroupStatus
from datetime import datetime
from typing import Optional, List


class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self, 
        service: Optional[str] = None, 
        environment: Optional[str] = None,
        status: Optional[GroupStatus] = None,
        since: Optional[datetime] = None, 
        until: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ):
        """List error groups with enhanced filtering"""
        q = select(ErrorGroup)
        
        # Apply filters
        conditions = []
        if service:
            conditions.append(ErrorGroup.service == service)
        if environment:
            conditions.append(ErrorGroup.environment == environment)
        if status:
            conditions.append(ErrorGroup.status == status)
        if since:
            conditions.append(ErrorGroup.last_seen >= since)
        if until:
            conditions.append(ErrorGroup.last_seen <= until)
        
        if conditions:
            q = q.where(and_(*conditions))
        
        # Order by last seen descending and apply pagination
        q = q.order_by(desc(ErrorGroup.last_seen)).offset(offset).limit(limit)
        
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_by_fingerprint(self, fingerprint: str):
        """Get error group by fingerprint"""
        q = select(ErrorGroup).where(ErrorGroup.fingerprint == fingerprint)
        result = await self.session.execute(q)
        return result.scalars().first()
    
    async def get_by_id(self, group_id: int):
        """Get error group by ID"""
        q = select(ErrorGroup).where(ErrorGroup.id == group_id)
        result = await self.session.execute(q)
        return result.scalars().first()
    
    async def update_status(self, group_id: int, status: GroupStatus):
        """Update the status of an error group"""
        group = await self.get_by_id(group_id)
        if group:
            group.status = status
            await self.session.commit()
        return group
    
    async def get_stats(
        self,
        service: Optional[str] = None,
        environment: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ):
        """Get error group statistics"""
        # Base query
        base_query = select(ErrorGroup)
        conditions = []
        
        # Apply filters
        if service:
            conditions.append(ErrorGroup.service == service)
        if environment:
            conditions.append(ErrorGroup.environment == environment)
        if since:
            conditions.append(ErrorGroup.last_seen >= since)
        if until:
            conditions.append(ErrorGroup.last_seen <= until)
        
        if conditions:
            base_query = base_query.where(and_(*conditions))
        
        # Get total groups
        total_query = select(ErrorGroup).select_from(base_query.subquery())
        total_result = await self.session.execute(total_query)
        total_groups = len(total_result.scalars().all())
        
        # Get groups by status
        unresolved_query = select(ErrorGroup).where(
            and_(*conditions, ErrorGroup.status == GroupStatus.UNRESOLVED)
        ) if conditions else select(ErrorGroup).where(ErrorGroup.status == GroupStatus.UNRESOLVED)
        
        unresolved_result = await self.session.execute(unresolved_query)
        unresolved_groups = len(unresolved_result.scalars().all())
        
        return {
            "total_groups": total_groups,
            "unresolved_groups": unresolved_groups,
            "resolved_groups": total_groups - unresolved_groups,
        }

from datetime import datetime
from typing import Optional, List
from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.groups import ErrorGroup, GroupStatus


class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(
        self, 
        project_id: int,
        service: Optional[str] = None, 
        environment: Optional[str] = None,
        status: Optional[GroupStatus] = None,
        since: Optional[datetime] = None, 
        until: Optional[datetime] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[ErrorGroup]:
        """List error groups with filtering"""
        query = select(ErrorGroup).where(ErrorGroup.project_id == project_id)
        
        if service:
            query = query.where(ErrorGroup.service == service)
        if environment:
            query = query.where(ErrorGroup.environment == environment)
        if status:
            query = query.where(ErrorGroup.status == status)
        if since:
            query = query.where(ErrorGroup.last_seen >= since)
        if until:
            query = query.where(ErrorGroup.last_seen <= until)
        
        query = query.order_by(ErrorGroup.last_seen.desc())
        query = query.limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())
        
    async def get_by_fingerprint(self, project_id: int, fingerprint: str) -> Optional[ErrorGroup]:
        """Get error group by fingerprint"""
        result = await self.session.execute(
            select(ErrorGroup).where(
                and_(
                    ErrorGroup.project_id == project_id,
                    ErrorGroup.fingerprint == fingerprint
                )
            )
        )
        return result.scalar_one_or_none()
    
    async def get_by_id(self, group_id: int):
        """Get error group by ID"""
        q = select(ErrorGroup).where(ErrorGroup.id == group_id)
        result = await self.session.execute(q)
        return result.scalars().first()
    
    async def update_status(self, group_id: int, status: GroupStatus) -> Optional[ErrorGroup]:
        """Update error group status"""
        group = await self.session.get(ErrorGroup, group_id)
        if group:
            group.status = status
            await self.session.commit()
        return group
    
    async def get_stats(
        self,
        project_id: int,
        service: Optional[str] = None,
        environment: Optional[str] = None,
        since: Optional[datetime] = None,
        until: Optional[datetime] = None
    ) -> dict:
        """Get error group statistics"""
        query = select(
            func.count().label('total_groups'),
            func.count().filter(ErrorGroup.status == GroupStatus.UNRESOLVED).label('unresolved_groups'),
            func.count().filter(ErrorGroup.status == GroupStatus.RESOLVED).label('resolved_groups')
        ).where(ErrorGroup.project_id == project_id)
        
        if service:
            query = query.where(ErrorGroup.service == service)
        if environment:
            query = query.where(ErrorGroup.environment == environment)
        if since:
            query = query.where(ErrorGroup.last_seen >= since)
        if until:
            query = query.where(ErrorGroup.last_seen <= until)
        
        result = await self.session.execute(query)
        row = result.one()
        return {
            'total_groups': row.total_groups,
            'unresolved_groups': row.unresolved_groups,
            'resolved_groups': row.resolved_groups
        }

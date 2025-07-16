from datetime import datetime
from typing import Optional, List
from db.repositories.groups import GroupRepository
from db.repositories.projects import ProjectRepository
from db.models.groups import GroupStatus
from api.groups.schema import GroupOut, GroupDetailOut
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

class GroupService:
    def __init__(self, session: AsyncSession):
        self.repo = GroupRepository(session=session)
        self.project_repo = ProjectRepository(session=session)

    async def _verify_project(self, project_id: int) -> None:
        """Verify project exists and is active"""
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not project.is_active:
            raise HTTPException(status_code=400, detail="Project is not active")

    async def list_groups(
        self, 
        project_id: int,
        service: Optional[str] = None, 
        environment: Optional[str] = None,
        status: Optional[str] = None,
        since: Optional[str] = None, 
        until: Optional[str] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[GroupOut]:
        """List error groups with enhanced filtering"""
        await self._verify_project(project_id)
        
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
            project_id=project_id,
            service=service,
            environment=environment,
            status=status_enum,
            since=since_dt,
            until=until_dt,
            limit=limit,
            offset=offset
        )
        return [GroupOut(**g.model_dump()) for g in groups]

    async def get_group(self, project_id: int, fingerprint: str) -> GroupDetailOut:
        """Get error group by fingerprint"""
        await self._verify_project(project_id)
        
        group = await self.repo.get_by_fingerprint(project_id, fingerprint)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        
        # For MVP, we'll leave recent_events empty
        # In a full implementation, you'd fetch recent errors for this group
        return GroupDetailOut(**group.model_dump())
    
    async def update_group_status(self, project_id: int, fingerprint: str, status: str) -> GroupOut:
        """Update the status of an error group"""
        await self._verify_project(project_id)
        
        group = await self.repo.get_by_fingerprint(project_id, fingerprint)
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
        project_id: int,
        service: Optional[str] = None,
        environment: Optional[str] = None,
        since: Optional[str] = None,
        until: Optional[str] = None
    ):
        """Get error group statistics"""
        await self._verify_project(project_id)
        
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
            project_id=project_id,
            service=service,
            environment=environment,
            since=since_dt,
            until=until_dt
        )

from fastapi import status, Depends, Query, Path
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional

from db.session import get_db_session
from api.groups.service import GroupService
from api.groups.schema import GroupOut, GroupDetailOut, GroupStatusUpdate, GroupStats

router = InferringRouter(prefix="/projects/{project_id}/groups", tags=["groups"])

@cbv(router)
class GroupController:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.service = GroupService(session=session)

    @router.get("/", response_model=list[GroupOut], status_code=status.HTTP_200_OK)
    async def list_groups(
        self,
        project_id: int = Path(..., description="Project ID"),
        service: Optional[str] = Query(None, description="Filter by service name"),
        environment: Optional[str] = Query(None, description="Filter by environment"),
        status: Optional[str] = Query(None, description="Filter by status (unresolved, resolved, ignored)"),
        since: Optional[str] = Query(None, description="ISO datetime, inclusive"),
        until: Optional[str] = Query(None, description="ISO datetime, inclusive"),
        limit: int = Query(100, ge=1, le=1000, description="Number of groups to return"),
        offset: int = Query(0, ge=0, description="Number of groups to skip")
    ):
        """List error groups with enhanced filtering"""
        return await self.service.list_groups(
            project_id=project_id,
            service=service,
            environment=environment,
            status=status,
            since=since,
            until=until,
            limit=limit,
            offset=offset
        )

    @router.get("/{fingerprint}", response_model=GroupDetailOut, status_code=status.HTTP_200_OK)
    async def get_group(
        self,
        project_id: int = Path(..., description="Project ID"),
        fingerprint: str = Path(..., description="Group fingerprint")
    ):
        """Get error group details by fingerprint"""
        return await self.service.get_group(project_id, fingerprint)
    
    @router.put("/{fingerprint}/status", response_model=GroupOut, status_code=status.HTTP_200_OK)
    async def update_group_status(
        self, 
        status_update: GroupStatusUpdate,
        project_id: int = Path(..., description="Project ID"),
        fingerprint: str = Path(..., description="Group fingerprint")
    ):
        """Update the status of an error group"""
        return await self.service.update_group_status(project_id, fingerprint, status_update.status)
    
    @router.get("/stats", response_model=GroupStats, status_code=status.HTTP_200_OK)
    async def get_group_stats(
        self,
        project_id: int = Path(..., description="Project ID"),
        service: Optional[str] = Query(None, description="Filter by service name"),
        environment: Optional[str] = Query(None, description="Filter by environment"),
        since: Optional[str] = Query(None, description="ISO datetime, inclusive"),
        until: Optional[str] = Query(None, description="ISO datetime, inclusive")
    ):
        """Get error group statistics"""
        return await self.service.get_group_stats(
            project_id=project_id,
            service=service,
            environment=environment,
            since=since,
            until=until
        )

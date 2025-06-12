from fastapi import status, Depends, Query
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from api.groups.service import GroupService
from api.groups.schema import GroupOut, GroupDetailOut

router = InferringRouter(prefix="/groups", tags=["groups"])

@cbv(router)
class GroupController:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.service = GroupService(session=session)

    @router.get("/", response_model=list[GroupOut], status_code=status.HTTP_200_OK)
    async def list_groups(
        self,
        service: str | None = Query(None, description="Filter by service name"),
        since: str | None = Query(None, description="ISO datetime, inclusive"),
        until: str | None = Query(None, description="ISO datetime, inclusive"),
    ):
        return await self.service.list_groups(service=service, since=since, until=until)

    @router.get("/{fingerprint}", response_model=GroupDetailOut, status_code=status.HTTP_200_OK)
    async def get_group(self, fingerprint: str):
        return await self.service.get_group(fingerprint)

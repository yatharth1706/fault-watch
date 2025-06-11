from db.repositories.groups import GroupRepository
from api.groups.schema import GroupOut, GroupDetailOut
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

class GroupService:
    def __init__(self, session: AsyncSession):
        self.repo = GroupRepository(session=session)

    async def list_groups(self, service: str | None = None, since: str | None = None, until: str | None = None) -> list[GroupOut]:
        # optionally parse since/until ISO strings into datetimes
        groups = await self.repo.list(service=service, since=since, until=until)
        return [GroupOut(**g.model_dump()) for g in groups]

    async def get_group(self, fingerprint: str) -> GroupDetailOut:
        group = await self.repo.get_by_fingerprint(fingerprint)
        if not group:
            raise HTTPException(status_code=404, detail="Group not found")
        # stub recent_events; in Phase 1 we can leave it empty or fetch from errors_raw
        return GroupDetailOut(**group.model_dump())

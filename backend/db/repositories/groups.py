from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db.models.groups import ErrorGroup
from datetime import datetime

class GroupRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def list(self, service: str | None = None, since: datetime | None = None, until: datetime | None = None):
        q = select(ErrorGroup)
        if service:
            q = q.filter(ErrorGroup.service == service)
        if since:
            q = q.filter(ErrorGroup.last_seen >= since)
        if until:
            q = q.filter(ErrorGroup.last_seen <= until)
        q = q.order_by(ErrorGroup.last_seen.desc())
        result = await self.session.execute(q)
        return result.scalars().all()

    async def get_by_fingerprint(self, fingerprint: str):
        q = select(ErrorGroup).where(ErrorGroup.fingerprint == fingerprint)
        result = await self.session.execute(q)
        return result.scalars().first()

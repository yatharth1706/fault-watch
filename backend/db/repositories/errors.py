from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.errors import RawError

class ErrorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_errors(self):
        result = await self.session.execute(
            select(RawError).order_by(RawError.received_at.desc()).limit(100)
        )
        return result.scalars().all()
    
    async def ingest_error(self, error: RawError):
        self.session.add(error)
        await self.session.commit()
        return {"status": "accepted"}
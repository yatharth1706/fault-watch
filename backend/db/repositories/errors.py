from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.errors import RawError


class ErrorRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_errors_by_project(self, project_id: int) -> list[RawError]:
        """Get all errors for a specific project"""
        result = await self.session.execute(
            select(RawError)
            .where(RawError.project_id == project_id)
            .order_by(RawError.timestamp.desc())
        )
        return list(result.scalars().all())
    
    async def ingest_error(self, error: RawError) -> RawError:
        """Save a new error"""
        self.session.add(error)
        await self.session.commit()
        return error
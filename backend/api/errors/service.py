from db.repositories.errors import ErrorRepository
from .schema import ErrorPayload
from db.models.errors import RawError
from sqlalchemy.ext.asyncio import AsyncSession


class ErrorService:
    def __init__(self, session: AsyncSession):
        self.error_repository = ErrorRepository(session=session)
        
    async def get_errors(self):
        errors = await self.error_repository.get_errors()
        return [ErrorPayload(**error.model_dump()) for error in errors]

    async def ingest_error(self, payload: ErrorPayload):
        raw_error = RawError(
            service=payload.service,
            error_type=payload.error_type,
            message=payload.message,
            stack_trace=payload.stack_trace,
            error_metadata=payload.error_metadata
        )
        return await self.error_repository.ingest_error(raw_error)
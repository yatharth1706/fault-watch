from datetime import datetime
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
        # Create raw error record with new fields
        raw_error = RawError(
            # Project and environment
            service=payload.service,
            environment=payload.environment,
            
            # Error details
            message=payload.message,
            level=payload.level.value,
            
            # Exception information
            exception_type=payload.exception.type if payload.exception else None,
            exception_value=payload.exception.value if payload.exception else None,
            exception_module=payload.exception.module if payload.exception else None,
            
            # Context
            tags=payload.tags,
            extra=payload.extra,
            
            # User context
            user_id=payload.user.id if payload.user else None,
            user_username=payload.user.username if payload.user else None,
            user_email=payload.user.email if payload.user else None,
            user_ip=payload.user.ip_address if payload.user else None,
            
            # Request context
            request_method=payload.request.method if payload.request else None,
            request_url=payload.request.url if payload.request else None,
            request_headers=payload.request.headers if payload.request else None,
            request_data=payload.request.data if payload.request else None,
            
            # Metadata
            timestamp=payload.timestamp or datetime.utcnow(),
            release=payload.release,
            
            # Legacy fields for backward compatibility
            error_type=payload.error_type,
            stack_trace=payload.stack_trace,
            error_metadata=payload.error_metadata,
        )
        
        return await self.error_repository.ingest_error(raw_error)

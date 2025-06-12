from datetime import datetime
from db.repositories.errors import ErrorRepository
from db.repositories.groups import GroupRepository
from .schema import ErrorPayload
from .fingerprinting import ErrorFingerprinter
from db.models.errors import RawError
from db.models.groups import ErrorGroup, GroupStatus
from sqlalchemy.ext.asyncio import AsyncSession


class ErrorService:
    def __init__(self, session: AsyncSession):
        self.error_repository = ErrorRepository(session=session)
        self.group_repository = GroupRepository(session=session)
        self.fingerprinter = ErrorFingerprinter()
        
    async def get_errors(self):
        errors = await self.error_repository.get_errors()
        return [ErrorPayload(**error.model_dump()) for error in errors]

    async def ingest_error(self, payload: ErrorPayload):
        # Generate fingerprint and grouping information
        fingerprint = self.fingerprinter.generate_fingerprint(payload)
        title = self.fingerprinter.generate_title(payload)
        culprit = self.fingerprinter.generate_culprit(payload)
        grouping_key = self.fingerprinter.get_grouping_key(payload)
        
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
        
        # Save the error first
        await self.error_repository.ingest_error(raw_error)
        
        # Process error grouping
        await self._process_error_grouping(raw_error, payload, fingerprint, title, culprit, grouping_key)
        
        return {
            "status": "accepted",
            "fingerprint": fingerprint,
            "error_id": raw_error.id
        }
    
    async def _process_error_grouping(
        self, 
        raw_error: RawError, 
        payload: ErrorPayload, 
        fingerprint: str, 
        title: str, 
        culprit: str, 
        grouping_key: str
    ):
        """Process error for grouping with existing error groups"""
        
        # Check if group already exists
        existing_group = await self.group_repository.get_by_fingerprint(fingerprint)
        
        if existing_group:
            # Update existing group
            existing_group.occurrences += 1
            existing_group.last_seen = raw_error.timestamp
            
            # Update user impact if this is a new user
            if payload.user and payload.user.id:
                # For MVP, we'll just increment users_affected
                # In a full implementation, you'd track unique users
                existing_group.users_affected += 1
        else:
            # Create new group
            new_group = ErrorGroup(
                fingerprint=fingerprint,
                grouping_key=grouping_key,
                service=payload.service,
                environment=payload.environment,
                title=title,
                culprit=culprit,
                level=payload.level.value,
                status=GroupStatus.UNRESOLVED,
                first_seen=raw_error.timestamp,
                last_seen=raw_error.timestamp,
                occurrences=1,
                users_affected=1 if payload.user and payload.user.id else 0,
                example_message=payload.message,  # Legacy field
            )
            
            # Save the new group
            self.group_repository.session.add(new_group)
            await self.group_repository.session.flush()  # Get the ID
        
        # Mark error as processed
        raw_error.processed = True
        
        # Commit all changes
        await self.group_repository.session.commit()

from typing import Dict, Any
import asyncio
from celery import Task
from celery_app.main import celery
from api.errors.fingerprinting import ErrorFingerprinter
from db.models.errors import RawError
from db.models.groups import ErrorGroup
from db.session import async_session
from sqlalchemy import select
from api.errors.schema import ErrorPayload


class DatabaseTask(Task):
    """Custom task class that provides a database session."""
    _fingerprinter: ErrorFingerprinter = None

    @property
    def fingerprinter(self) -> ErrorFingerprinter:
        if self._fingerprinter is None:
            self._fingerprinter = ErrorFingerprinter()
        return self._fingerprinter

    async def _run_async(self, coro):
        """Helper method to run async code in sync context"""
        return await coro

    def run(self, *args, **kwargs):
        """Override run to handle async operations"""
        return asyncio.run(self._run_async(self._run_task(*args, **kwargs)))

    async def _run_task(self, *args, **kwargs):
        """Actual task implementation"""
        raise NotImplementedError("Subclasses must implement _run_task")


@celery.task(base=DatabaseTask, bind=True)
class ProcessErrorTask(DatabaseTask):
    async def _run_task(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming error:
        1. Get raw error from database
        2. Generate fingerprint and grouping information
        3. Find or create error group
        4. Create error event
        5. Update group statistics
        """
        async with async_session() as session:
            try:
                # Get the raw error from database
                raw_error_query = select(RawError).where(RawError.id == error_data["raw_error_id"])
                result = await session.execute(raw_error_query)
                raw_error = result.scalar_one_or_none()
                
                if not raw_error:
                    raise ValueError(f"Raw error {error_data['raw_error_id']} not found")
                
                # Convert payload back to ErrorPayload for fingerprinting
                payload = ErrorPayload(**error_data["payload"])
                
                # Generate fingerprint and grouping information
                fingerprint = self.fingerprinter.generate_fingerprint(payload)
                title = self.fingerprinter.generate_title(payload)
                culprit = self.fingerprinter.generate_culprit(payload)
                grouping_key = self.fingerprinter.get_grouping_key(payload)
                
                # Find or create error group
                group_query = select(ErrorGroup).where(ErrorGroup.fingerprint == fingerprint)
                result = await session.execute(group_query)
                group = result.scalar_one_or_none()
                
                if not group:
                    group = ErrorGroup(
                        fingerprint=fingerprint,
                        grouping_key=grouping_key,
                        service=raw_error.service,
                        environment=raw_error.environment,
                        title=title,
                        culprit=culprit,
                        level=raw_error.level,
                        status="unresolved",
                        first_seen=raw_error.timestamp,
                        last_seen=raw_error.timestamp,
                        occurrences=1,
                        users_affected=1 if raw_error.user_id else 0,
                        example_message=raw_error.message,
                    )
                    session.add(group)
                    await session.flush()
                else:
                    # Update existing group
                    group.occurrences += 1
                    group.last_seen = raw_error.timestamp
                    
                    # Update user impact if this is a new user
                    if raw_error.user_id:
                        group.users_affected += 1
                
                # Create error event
                # event = ErrorEvent(
                #     group_id=group.id,
                #     raw_error_id=raw_error.id,
                #     payload=error_data["payload"],
                #     timestamp=raw_error.timestamp
                # )
                # session.add(event)
                
                # Mark raw error as processed
                raw_error.processed = True
                
                await session.commit()
                
                # Return group ID for follow-up tasks
                return {
                    "group_id": group.id,
                    "fingerprint": fingerprint,
                    "status": "processed"
                }
                
            except Exception as e:
                await session.rollback()
                # Re-raise the exception to trigger Celery's retry mechanism
                raise self.retry(exc=e, countdown=60, max_retries=3)


@celery.task(base=DatabaseTask, bind=True)
class DeduplicateErrorsTask(DatabaseTask):
    async def _run_task(self, group_id: int) -> Dict[str, Any]:
        """
        Deduplicate errors within a group based on similarity.
        This is a background task that can be scheduled periodically.
        """
        async with async_session() as session:
            try:
                # Get all events for the group
                group_query = select(ErrorGroup).where(ErrorGroup.id == group_id)
                result = await session.execute(group_query)
                group = result.scalar_one_or_none()
                
                if not group:
                    return {"status": "error", "message": "Group not found"}
                    
                # TODO: Implement deduplication logic here
                # This could involve:
                # 1. Comparing stack traces
                # 2. Looking for similar error messages
                # 3. Merging very similar events
                
                await session.commit()
                return {"status": "success", "group_id": group_id}
                
            except Exception as e:
                await session.rollback()
                raise self.retry(exc=e, countdown=300, max_retries=3)  # Retry every 5 minutes


@celery.task(base=DatabaseTask, bind=True)
class UpdateGroupStatisticsTask(DatabaseTask):
    async def _run_task(self, group_id: int) -> Dict[str, Any]:
        """
        Update error group statistics like:
        - Error frequency
        - User impact
        - Environment distribution
        """
        async with async_session() as session:
            try:
                # TODO: Implement statistics update logic
                # This could involve:
                # 1. Calculating error frequency over time
                # 2. Counting unique users affected
                # 3. Analyzing environment distribution
                
                await session.commit()
                return {"status": "success", "group_id": group_id}
                
            except Exception as e:
                await session.rollback()
                raise self.retry(exc=e, countdown=300, max_retries=3)


# Create task instances
process_error = ProcessErrorTask()
deduplicate_errors = DeduplicateErrorsTask()
update_group_statistics = UpdateGroupStatisticsTask() 
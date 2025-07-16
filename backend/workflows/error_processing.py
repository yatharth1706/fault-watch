from temporalio import workflow, activity

with workflow.unsafe.imports_passed_through():
    from datetime import timedelta, datetime
    from typing import Dict, Any, List
    from api.errors.fingerprinting import ErrorFingerprinter
    from api.errors.schema import ErrorPayload
    from sqlalchemy import select, func
    from db.models.errors import RawError, ErrorEvent
    from db.models.groups import ErrorGroup
    from db.session import async_session

@activity.defn
async def process_error_activity(error_data: Dict[str, Any]) -> Dict[str, Any]:
    """Process a single error and generate its fingerprint."""
    fingerprinter = ErrorFingerprinter()
    payload = ErrorPayload(**error_data["payload"])
    
    # Generate fingerprint and grouping information
    fingerprint = fingerprinter.generate_fingerprint(payload)
    title = fingerprinter.generate_title(payload)
    culprit = fingerprinter.generate_culprit(payload)
    grouping_key = fingerprinter.get_grouping_key(payload)
    
    session = async_session()
    try:
        # Find or create error group
        group_query = select(ErrorGroup).where(
            ErrorGroup.fingerprint == fingerprint,
            ErrorGroup.project_id == payload.project_id
        )
        result = await session.execute(group_query)
        group = result.scalar_one_or_none()
        
        if not group:
            group = ErrorGroup(
                project_id=payload.project_id,  # Add project_id here
                fingerprint=fingerprint,
                grouping_key=grouping_key,
                service=payload.service,
                environment=payload.environment,
                title=title,
                culprit=culprit,
                level=payload.level.value,
                first_seen=datetime.utcnow(),
                last_seen=datetime.utcnow(),
                occurrences=1,
                example_message=payload.message
            )
            session.add(group)
        else:
            group.last_seen = datetime.utcnow()
            group.occurrences += 1
        
        # Create error event
        event = ErrorEvent(
            raw_error_id=error_data["raw_error_id"],
            group_fingerprint=fingerprint,
            event_type="new" if not group else "reoccurrence",
            timestamp=datetime.utcnow()
        )
        session.add(event)
        
        await session.commit()
        
        return {
            "raw_error_id": error_data["raw_error_id"],
            "group_id": group.id,
            "fingerprint": fingerprint,
            "title": title,
            "culprit": culprit,
            "grouping_key": grouping_key,
        }
    finally:
        await session.close()

@activity.defn
async def deduplicate_errors_activity(group_fingerprint: str) -> Dict[str, Any]:
    """Deduplicate errors within a group."""
    session = async_session()
    try:
        # Get all error events in this group from the last hour
        one_hour_ago = datetime.utcnow() - timedelta(hours=1)
        events_query = select(ErrorEvent).where(
            ErrorEvent.group_fingerprint == group_fingerprint,
            ErrorEvent.timestamp >= one_hour_ago
        ).order_by(ErrorEvent.timestamp.desc())
        
        result = await session.execute(events_query)
        events = result.scalars().all()
        
        # Get the raw errors for these events
        raw_error_ids = [event.raw_error_id for event in events]
        raw_errors_query = select(RawError).where(RawError.id.in_(raw_error_ids))
        result = await session.execute(raw_errors_query)
        raw_errors = result.scalars().all()
        
        # Group errors by their exact stack trace and message
        duplicates: Dict[str, List[RawError]] = {}
        for error in raw_errors:
            key = f"{error.stack_trace}:{error.message}"
            if key not in duplicates:
                duplicates[key] = []
            duplicates[key].append(error)
        
        # Mark errors as duplicates if they share the same key
        duplicate_count = 0
        for errors in duplicates.values():
            if len(errors) > 1:
                # Keep the first error as primary, mark others as duplicates
                primary = errors[0]
                for duplicate in errors[1:]:
                    duplicate.is_duplicate = True
                    duplicate.duplicate_of_id = primary.id
                    duplicate_count += 1
        
        await session.commit()
        
        return {
            "group_fingerprint": group_fingerprint,
            "duplicates_found": duplicate_count,
            "total_errors_processed": len(raw_errors)
        }
    finally:
        await session.close()

@activity.defn
async def update_group_statistics_activity(group_fingerprint: str) -> Dict[str, Any]:
    """Update error group statistics."""
    session = async_session()
    try:
        # Get the error group
        group_query = select(ErrorGroup).where(ErrorGroup.fingerprint == group_fingerprint)
        result = await session.execute(group_query)
        group = result.scalar_one_or_none()
        
        if not group:
            return {"group_fingerprint": group_fingerprint, "updated": False, "error": "Group not found"}
        
        # Calculate statistics
        stats_query = select(
            func.count(ErrorEvent.id).label('total_events'),
            func.min(ErrorEvent.timestamp).label('first_seen'),
            func.max(ErrorEvent.timestamp).label('last_seen')
        ).where(ErrorEvent.group_fingerprint == group_fingerprint)
        
        result = await session.execute(stats_query)
        stats = result.mappings().first()
        
        # Update group statistics
        group.occurrences = stats['total_events']
        group.first_seen = stats['first_seen']
        group.last_seen = stats['last_seen']
        
        # Calculate frequency (events per hour) over the last 24 hours
        day_ago = datetime.utcnow() - timedelta(days=1)
        recent_count_query = select(
            func.count(ErrorEvent.id)
        ).where(
            ErrorEvent.group_fingerprint == group_fingerprint,
            ErrorEvent.timestamp >= day_ago
        )
        result = await session.execute(recent_count_query)
        recent_count = result.scalar()
        
        group.frequency = recent_count / 24  # events per hour
        
        # Update status based on frequency
        if group.frequency > 10:  # More than 10 events per hour
            group.status = 'critical'
        elif group.frequency > 1:  # More than 1 event per hour
            group.status = 'warning'
        else:
            group.status = 'stable'
        
        await session.commit()
        
        return {
            "group_fingerprint": group_fingerprint,
            "updated": True,
            "total_occurrences": group.occurrences,
            "frequency": group.frequency,
            "status": group.status
        }
    finally:
        await session.close()

@workflow.defn
class ErrorProcessingWorkflow:
    @workflow.run
    async def run(self, error_data: Dict[str, Any]) -> Dict[str, Any]:
        # Process the error
        process_result = await workflow.execute_activity(
            process_error_activity,
            error_data,
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        # Run deduplication after a delay
        dedupe_result = await workflow.execute_activity(
            deduplicate_errors_activity,
            process_result["fingerprint"],
            start_to_close_timeout=timedelta(minutes=5),
            schedule_to_start_timeout=timedelta(minutes=5)
        )
        
        # Update group statistics
        stats_result = await workflow.execute_activity(
            update_group_statistics_activity,
            process_result["fingerprint"],
            start_to_close_timeout=timedelta(minutes=5)
        )
        
        return {
            "error_id": process_result["raw_error_id"],
            "group_id": process_result["group_id"],
            "fingerprint": process_result["fingerprint"],
            "deduplication_result": dedupe_result,
            "statistics_updated": stats_result["updated"],
            "status": stats_result.get("status")
        } 
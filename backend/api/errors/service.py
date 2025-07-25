from datetime import datetime, timedelta
from temporalio.client import Client
from db.repositories.errors import ErrorRepository
from db.repositories.groups import GroupRepository
from db.repositories.projects import ProjectRepository
from .schema import ErrorPayload
from db.models.errors import RawError
from sqlalchemy.ext.asyncio import AsyncSession
from temporal_config import temporal_settings
from workflows.error_processing import ErrorProcessingWorkflow
from fastapi import HTTPException


class ErrorService:
    def __init__(self, session: AsyncSession):
        self.error_repository = ErrorRepository(session=session)
        self.group_repository = GroupRepository(session=session)
        self.project_repository = ProjectRepository(session=session)
        
    async def get_errors(self, project_id: int):
        """Get errors for a specific project"""
        errors = await self.error_repository.get_errors_by_project(project_id)
        return [ErrorPayload(**error.model_dump()) for error in errors]

    async def ingest_error(self, payload: ErrorPayload):
        # Verify project exists and is active
        project = await self.project_repository.get_by_id(payload.project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not project.is_active:
            raise HTTPException(status_code=400, detail="Project is not active")

        # Calculate expiration based on project retention
        expires_at = None
        if project.retention_days > 0:
            expires_at = datetime.utcnow() + timedelta(days=project.retention_days)

        # Create raw error record
        raw_error = RawError(
            # Project info
            project_id=payload.project_id,
            service=payload.service or project.name,
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
            expires_at=expires_at,
            
            # Legacy fields for backward compatibility
            error_type=payload.error_type,
            stack_trace=payload.stack_trace,
            error_metadata=payload.error_metadata,
        )
        
        # Save the error
        await self.error_repository.ingest_error(raw_error)
        
        # Start Temporal workflow
        client = await Client.connect(temporal_settings.host_port)
        
        error_data = {
            "raw_error_id": raw_error.id,
            "payload": payload.model_dump(),
        }
        
        workflow_handle = await client.start_workflow(
            ErrorProcessingWorkflow.run,
            error_data,
            id=f"error-processing-{raw_error.id}",
            task_queue=temporal_settings.task_queue,
        )
        
        return {
            "raw_error_id": raw_error.id,
            "workflow_id": workflow_handle.id,
            "workflow_run_id": workflow_handle.run_id
        }

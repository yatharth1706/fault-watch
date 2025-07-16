# api/errors/controller.py

from fastapi import Depends, status, Path, HTTPException
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from api.auth import validate_api_key
from .schema import ErrorPayload
from .service import ErrorService

router = InferringRouter(prefix="/projects/{project_id}/errors", tags=["errors"])

@cbv(router)
class ErrorController:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
    ):
        self.service = ErrorService(session=session)

    @router.get("/", status_code=status.HTTP_200_OK)
    async def get_errors(self, project_id: int = Path(..., description="Project ID")):
        """Get errors for a specific project"""
        return await self.service.get_errors(project_id)

    @router.post("/", status_code=status.HTTP_202_ACCEPTED, dependencies=[Depends(validate_api_key)])
    async def ingest_error(
        self,
        payload: ErrorPayload,
        project_id: int = Path(..., description="Project ID")
    ):
        """Ingest an error for a specific project"""
        # Ensure project_id in path matches payload
        if payload.project_id != project_id:
            raise HTTPException(
                status_code=400,
                detail="Project ID in path must match project_id in payload"
            )
        return await self.service.ingest_error(payload)

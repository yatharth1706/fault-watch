# api/errors/controller.py

from fastapi import Depends, status
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from .schema import ErrorPayload
from .service import ErrorService

router = InferringRouter(prefix="/errors", tags=["errors"])

@cbv(router)
class ErrorController:
    def __init__(
        self,
        session: AsyncSession = Depends(get_db_session),
    ):
        self.service = ErrorService(session=session)

    @router.get("/", status_code=status.HTTP_200_OK)
    async def get_errors(self):
        return await self.service.get_errors()

    @router.post("/", status_code=status.HTTP_202_ACCEPTED)
    async def ingest_error(self, payload: ErrorPayload):
        return await self.service.ingest_error(payload)

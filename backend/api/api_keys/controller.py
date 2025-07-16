from fastapi import Depends, status, Path
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from .service import APIKeyService
from .schema import APIKeyCreate, APIKeyOut, APIKeyWithSecret

router = InferringRouter(prefix="/projects/{project_id}/api-keys", tags=["api-keys"])

@cbv(router)
class APIKeyController:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.service = APIKeyService(session=session)

    @router.post("/", response_model=APIKeyWithSecret, status_code=status.HTTP_201_CREATED)
    async def create_key(
        self,
        data: APIKeyCreate,
        project_id: int = Path(..., description="Project ID")
    ):
        """Create a new API key for a project"""
        key_data, raw_key = await self.service.create_key(project_id, data)
        return {**key_data, "key": raw_key}

    @router.get("/", response_model=list[APIKeyOut])
    async def list_keys(
        self,
        project_id: int = Path(..., description="Project ID")
    ):
        """List all API keys for a project"""
        return await self.service.list_project_keys(project_id)

    @router.delete("/{key_id}", response_model=APIKeyOut, status_code=status.HTTP_200_OK)
    async def deactivate_key(
        self,
        project_id: int = Path(..., description="Project ID"),
        key_id: int = Path(..., description="API Key ID")
    ):
        """Deactivate an API key"""
        return await self.service.deactivate_key(project_id, key_id) 
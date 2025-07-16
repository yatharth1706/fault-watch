from fastapi import Depends, status, Path, Query
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from .service import OrganizationService
from .schema import OrganizationCreate, OrganizationUpdate, OrganizationOut

router = InferringRouter(prefix="/organizations", tags=["organizations"])

@cbv(router)
class OrganizationController:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.service = OrganizationService(session=session)

    @router.post("/", response_model=OrganizationOut, status_code=status.HTTP_201_CREATED)
    async def create_organization(self, data: OrganizationCreate):
        """Create a new organization"""
        return await self.service.create_organization(data)

    @router.get("/{org_id}", response_model=OrganizationOut)
    async def get_organization(self, org_id: int = Path(..., description="Organization ID")):
        """Get organization by ID"""
        return await self.service.get_organization(org_id)

    @router.get("/", response_model=list[OrganizationOut])
    async def list_organizations(
        self,
        limit: int = Query(100, ge=1, le=1000, description="Number of organizations to return"),
        offset: int = Query(0, ge=0, description="Number of organizations to skip")
    ):
        """List active organizations"""
        return await self.service.list_organizations(limit=limit, offset=offset)

    @router.patch("/{org_id}", response_model=OrganizationOut)
    async def update_organization(
        self,
        data: OrganizationUpdate,
        org_id: int = Path(..., description="Organization ID")
    ):
        """Update organization details"""
        return await self.service.update_organization(org_id, data) 
from fastapi import Depends, status, Path
from fastapi_utils.inferring_router import InferringRouter
from fastapi_utils.cbv import cbv
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from .service import ProjectService
from .schema import ProjectCreate, ProjectUpdate, ProjectOut

router = InferringRouter(prefix="/organizations/{org_id}/projects", tags=["projects"])

@cbv(router)
class ProjectController:
    def __init__(self, session: AsyncSession = Depends(get_db_session)):
        self.service = ProjectService(session=session)

    @router.post("/", response_model=ProjectOut, status_code=status.HTTP_201_CREATED)
    async def create_project(
        self,
        data: ProjectCreate,
        org_id: int = Path(..., description="Organization ID")
    ):
        """Create a new project"""
        return await self.service.create_project(org_id, data)

    @router.get("/{project_id}", response_model=ProjectOut)
    async def get_project(
        self,
        org_id: int = Path(..., description="Organization ID"),
        project_id: int = Path(..., description="Project ID")
    ):
        """Get project by ID"""
        return await self.service.get_project(org_id, project_id)

    @router.get("/", response_model=list[ProjectOut])
    async def list_projects(
        self,
        org_id: int = Path(..., description="Organization ID")
    ):
        """List all projects for an organization"""
        return await self.service.list_projects(org_id)

    @router.patch("/{project_id}", response_model=ProjectOut)
    async def update_project(
        self,
        data: ProjectUpdate,
        org_id: int = Path(..., description="Organization ID"),
        project_id: int = Path(..., description="Project ID")
    ):
        """Update project details"""
        return await self.service.update_project(org_id, project_id, data) 
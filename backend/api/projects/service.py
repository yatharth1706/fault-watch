from slugify import slugify
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.projects import ProjectRepository
from db.repositories.organizations import OrganizationRepository
from .schema import ProjectCreate, ProjectUpdate


class ProjectService:
    def __init__(self, session: AsyncSession):
        self.repo = ProjectRepository(session=session)
        self.org_repo = OrganizationRepository(session=session)

    async def _verify_organization(self, org_id: int) -> None:
        """Verify organization exists and is active"""
        org = await self.org_repo.get_by_id(org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        if not org.is_active:
            raise HTTPException(status_code=400, detail="Organization is not active")

    async def create_project(self, org_id: int, data: ProjectCreate):
        """Create a new project"""
        # Verify organization exists and is active
        await self._verify_organization(org_id)

        # Generate slug from name if not provided
        slug = data.slug or slugify(data.name)
        
        # Check if slug is already taken in this organization
        existing = await self.repo.get_by_slug(org_id, slug)
        if existing:
            raise HTTPException(status_code=400, detail="Project slug already exists in this organization")
        
        # Create project with defaults
        project = await self.repo.create(
            organization_id=org_id,
            name=data.name,
            slug=slug,
            platform=data.platform,
            retention_days=data.retention_days or 90
        )
        return project

    async def get_project(self, org_id: int, project_id: int):
        """Get project by ID"""
        # Verify organization exists and is active
        await self._verify_organization(org_id)
        
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Project does not belong to this organization")
        return project

    async def list_projects(self, org_id: int):
        """List all projects for an organization"""
        # Verify organization exists and is active
        await self._verify_organization(org_id)
        
        return await self.repo.list_by_organization(org_id)

    async def update_project(self, org_id: int, project_id: int, data: ProjectUpdate):
        """Update project details"""
        # Verify organization exists and is active
        await self._verify_organization(org_id)
        
        # Get and verify project belongs to organization
        project = await self.repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if project.organization_id != org_id:
            raise HTTPException(status_code=403, detail="Project does not belong to this organization")
        
        update_data = data.model_dump(exclude_unset=True)
        if 'name' in update_data and not update_data.get('slug'):
            update_data['slug'] = slugify(update_data['name'])
        
        if 'slug' in update_data:
            existing = await self.repo.get_by_slug(org_id, update_data['slug'])
            if existing and existing.id != project_id:
                raise HTTPException(status_code=400, detail="Project slug already exists in this organization")
        
        updated_project = await self.repo.update(project_id, **update_data)
        return updated_project 
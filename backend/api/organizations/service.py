from uuid import UUID
from slugify import slugify
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.organizations import OrganizationRepository
from .schema import OrganizationCreate, OrganizationOut, OrganizationUpdate


class OrganizationService:
    def __init__(self, session: AsyncSession):
        self.repo = OrganizationRepository(session=session)

    async def create_organization(self, data: OrganizationCreate) -> OrganizationOut:
        """Create a new organization"""
        # Generate slug from name if not provided
        slug = data.slug or slugify(data.name)
        
        # Check if slug is already taken
        existing = await self.repo.get_by_slug(slug)
        if existing:
            raise HTTPException(status_code=400, detail="Organization slug already exists")
        
        org = await self.repo.create(name=data.name, slug=slug)
        return OrganizationOut.model_validate(org)

    async def get_organization(self, org_id: int):
        """Get organization by ID"""
        org = await self.repo.get_by_id(org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        return org

    async def list_organizations(self, limit: int = 100, offset: int = 0):
        """List active organizations"""
        return await self.repo.list_active(limit=limit, offset=offset)

    async def update_organization(self, org_id: int, data: OrganizationUpdate):
        """Update organization details"""
        org = await self.repo.get_by_id(org_id)
        if not org:
            raise HTTPException(status_code=404, detail="Organization not found")
        
        update_data = data.model_dump(exclude_unset=True)
        if 'name' in update_data and not update_data.get('slug'):
            update_data['slug'] = slugify(update_data['name'])
        
        if 'slug' in update_data:
            existing = await self.repo.get_by_slug(update_data['slug'])
            if existing and existing.id != org_id:
                raise HTTPException(status_code=400, detail="Organization slug already exists")
        
        updated_org = await self.repo.update(org_id, **update_data)
        return updated_org 
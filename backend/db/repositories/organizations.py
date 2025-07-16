from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.organizations import Organization


class OrganizationRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create(self, name: str, slug: str) -> Organization:
        """Create a new organization"""
        org = Organization(name=name, slug=slug)
        self.session.add(org)
        await self.session.commit()
        return org

    async def get_by_id(self, org_id: int) -> Organization | None:
        """Get organization by ID"""
        result = await self.session.execute(
            select(Organization).where(Organization.id == org_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, slug: str) -> Organization | None:
        """Get organization by slug"""
        result = await self.session.execute(
            select(Organization).where(Organization.slug == slug)
        )
        return result.scalar_one_or_none()

    async def list_active(self, limit: int = 100, offset: int = 0) -> list[Organization]:
        """List active organizations"""
        result = await self.session.execute(
            select(Organization)
            .where(Organization.is_active == True)
            .order_by(Organization.name)
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update(self, org_id: int, **kwargs) -> Organization | None:
        """Update organization fields"""
        org = await self.get_by_id(org_id)
        if org:
            for key, value in kwargs.items():
                setattr(org, key, value)
            await self.session.commit()
        return org 
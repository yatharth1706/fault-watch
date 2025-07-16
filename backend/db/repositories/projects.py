from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.projects import Project


class ProjectRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_by_id(self, project_id: int) -> Project | None:
        """Get a project by ID"""
        result = await self.session.execute(
            select(Project).where(Project.id == project_id)
        )
        return result.scalar_one_or_none()

    async def get_by_slug(self, organization_id: int, slug: str) -> Project | None:
        """Get a project by organization ID and slug"""
        result = await self.session.execute(
            select(Project).where(
                Project.organization_id == organization_id,
                Project.slug == slug
            )
        )
        return result.scalar_one_or_none()

    async def list_by_organization(self, organization_id: int) -> list[Project]:
        """List all projects for an organization"""
        result = await self.session.execute(
            select(Project)
            .where(Project.organization_id == organization_id)
            .order_by(Project.name)
        )
        return list(result.scalars().all())

    async def create(
        self,
        organization_id: int,
        name: str,
        slug: str,
        platform: str | None = None,
        retention_days: int = 90
    ) -> Project:
        """Create a new project"""
        project = Project(
            organization_id=organization_id,
            name=name,
            slug=slug,
            platform=platform,
            retention_days=retention_days
        )
        self.session.add(project)
        await self.session.commit()
        return project

    async def update(self, project_id: int, **kwargs) -> Project:
        """Update project attributes"""
        project = await self.get_by_id(project_id)
        assert project is not None  # We know project exists as this is called after get_by_id check
        for key, value in kwargs.items():
            setattr(project, key, value)
        await self.session.commit()
        return project 
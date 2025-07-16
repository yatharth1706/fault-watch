from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from db.repositories.api_keys import APIKeyRepository
from db.repositories.projects import ProjectRepository
from .schema import APIKeyCreate


class APIKeyService:
    def __init__(self, session: AsyncSession):
        self.repo = APIKeyRepository(session=session)
        self.project_repo = ProjectRepository(session=session)

    async def create_key(self, project_id: int, data: APIKeyCreate) -> tuple[dict, str]:
        """Create a new API key"""
        # Verify project exists and is active
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        if not project.is_active:
            raise HTTPException(status_code=400, detail="Project is not active")
        
        # Create API key
        api_key, raw_key = await self.repo.create(
            project_id=project_id,
            name=data.name
        )
        
        # Return both the API key model and the raw key
        # Raw key is only shown once at creation
        return {
            "id": api_key.id,
            "name": api_key.name,
            "prefix": api_key.prefix,
            "created_at": api_key.created_at,
            "is_active": api_key.is_active,
            "last_used_at": api_key.last_used_at,
            "expires_at": api_key.expires_at,
        }, raw_key

    async def list_project_keys(self, project_id: int):
        """List all API keys for a project"""
        # Verify project exists
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        return await self.repo.list_by_project(project_id)

    async def deactivate_key(self, project_id: int, key_id: int):
        """Deactivate an API key"""
        # Verify project exists
        project = await self.project_repo.get_by_id(project_id)
        if not project:
            raise HTTPException(status_code=404, detail="Project not found")
        
        # Get and verify API key belongs to project
        api_key = await self.repo.get_by_id(key_id)
        if not api_key:
            raise HTTPException(status_code=404, detail="API key not found")
        if api_key.project_id != project_id:
            raise HTTPException(status_code=403, detail="API key does not belong to this project")
        
        return await self.repo.deactivate(key_id)

    async def validate_key(self, key: str):
        """Validate an API key"""
        api_key = await self.repo.validate_key(key)
        if not api_key:
            raise HTTPException(status_code=401, detail="Invalid API key")
        if not api_key.is_active:
            raise HTTPException(status_code=401, detail="API key is not active")
        
        return api_key 
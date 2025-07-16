import secrets
import hashlib
from datetime import datetime, timezone
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from db.models.api_keys import APIKey


class APIKeyRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    def _generate_key(self) -> tuple[str, str, str]:
        """Generate a new API key, prefix, and hash"""
        # Generate a random 32-byte key
        key = secrets.token_urlsafe(32)
        # Use first 8 characters as prefix
        prefix = key[:8]
        # Hash the key for storage
        key_hash = hashlib.sha256(key.encode()).hexdigest()
        return key, prefix, key_hash

    def _hash_key(self, key: str) -> str:
        """Hash an API key for comparison"""
        return hashlib.sha256(key.encode()).hexdigest()

    async def create(self, project_id: int, name: str) -> tuple[APIKey, str]:
        """Create a new API key and return both the model and the raw key"""
        key, prefix, key_hash = self._generate_key()
        
        api_key = APIKey(
            project_id=project_id,
            name=name,
            prefix=prefix,
            key_hash=key_hash
        )
        
        self.session.add(api_key)
        await self.session.commit()
        
        return api_key, key

    async def get_by_id(self, key_id: int) -> APIKey | None:
        """Get API key by ID"""
        result = await self.session.execute(
            select(APIKey).where(APIKey.id == key_id)
        )
        return result.scalar_one_or_none()

    async def list_by_project(self, project_id: int) -> list[APIKey]:
        """List all API keys for a project"""
        result = await self.session.execute(
            select(APIKey)
            .where(APIKey.project_id == project_id)
            .order_by(APIKey.created_at.desc())
        )
        return list(result.scalars().all())

    async def validate_key(self, key: str) -> APIKey | None:
        """Validate an API key and update last_used_at if valid"""
        if len(key) < 8:
            return None
            
        prefix = key[:8]
        key_hash = self._hash_key(key)
        
        result = await self.session.execute(
            select(APIKey).where(
                and_(
                    APIKey.prefix == prefix,
                    APIKey.key_hash == key_hash,
                    APIKey.is_active == True,
                    (APIKey.expires_at.is_(None) | (APIKey.expires_at > datetime.now(timezone.utc)))
                )
            )
        )
        
        api_key = result.scalar_one_or_none()
        if api_key:
            api_key.last_used_at = datetime.now(timezone.utc)
            await self.session.commit()
        
        return api_key

    async def deactivate(self, key_id: int) -> APIKey | None:
        """Deactivate an API key"""
        api_key = await self.get_by_id(key_id)
        if api_key:
            api_key.is_active = False
            await self.session.commit()
        return api_key 
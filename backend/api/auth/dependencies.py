from typing import Annotated
from fastapi import Depends, HTTPException, Header
from sqlalchemy.ext.asyncio import AsyncSession

from db.session import get_db_session
from api.api_keys.service import APIKeyService


async def validate_api_key(
    project_id: int,
    authorization: Annotated[str | None, Header()] = None,
    session: AsyncSession = Depends(get_db_session),
) -> None:
    """Validate API key from Authorization header"""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="API key required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format. Use 'Bearer YOUR_API_KEY'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    api_key = authorization.replace("Bearer ", "")
    api_key_service = APIKeyService(session=session)
    key = await api_key_service.validate_key(api_key)
    
    # Verify key belongs to the project
    if key.project_id != project_id:
        raise HTTPException(
            status_code=403,
            detail="API key does not belong to this project"
        ) 
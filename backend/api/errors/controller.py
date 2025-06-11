# api/errors/controller.py
from fastapi import APIRouter, Depends, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from api.db.models.errors import RawError
from api.db.session import get_db
from api.errors.schema import ErrorPayload

router = APIRouter(prefix="/errors", tags=["errors"])

@router.get("/", status_code=status.HTTP_200_OK)
async def get_errors(db: AsyncSession = Depends(get_db)):
    errors = await db.execute(select(RawError))
    return errors.scalars().all()

@router.post("/", status_code=status.HTTP_202_ACCEPTED)
async def ingest_error(payload: ErrorPayload, db: AsyncSession = Depends(get_db)):
    raw = RawError(**payload.model_dump())
    db.add(raw)
    await db.commit()
    return {"status": "accepted"}

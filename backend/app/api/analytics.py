from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.analytics.compute import compute_analytics
from app.models.schemas import AnalyticsOut

router = APIRouter()


@router.get("/analytics", response_model=list[AnalyticsOut])
async def get_analytics(
    window: int = Query(7, ge=2, le=200),
    db: AsyncSession = Depends(get_db),
):
    return await compute_analytics(db, window=window)

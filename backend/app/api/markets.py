from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.market import Asset, PriceRecord
from app.models.schemas import AssetOut, PriceRecordOut
from app.services.ingestion import fetch_and_store

router = APIRouter()


@router.get("/markets", response_model=list[AssetOut])
async def get_markets(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset))
    assets = result.scalars().all()

    out = []
    for asset in assets:
        rec_result = await db.execute(
            select(PriceRecord)
            .where(PriceRecord.asset_id == asset.id)
            .order_by(desc(PriceRecord.timestamp))
            .limit(1)
        )
        latest = rec_result.scalar_one_or_none()
        out.append(AssetOut(
            symbol=asset.symbol,
            name=asset.name,
            latest_price=latest.price if latest else None,
            latest_volume=latest.volume if latest else None,
            price_change_24h=latest.price_change_24h if latest else None,
        ))
    return out


@router.get("/prices", response_model=AssetOut)
async def get_prices(symbol: str = Query(...), db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset).where(Asset.symbol == symbol.upper()))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

    rec_result = await db.execute(
        select(PriceRecord)
        .where(PriceRecord.asset_id == asset.id)
        .order_by(desc(PriceRecord.timestamp))
        .limit(1)
    )
    latest = rec_result.scalar_one_or_none()
    return AssetOut(
        symbol=asset.symbol,
        name=asset.name,
        latest_price=latest.price if latest else None,
        latest_volume=latest.volume if latest else None,
        price_change_24h=latest.price_change_24h if latest else None,
    )


@router.get("/history", response_model=list[PriceRecordOut])
async def get_history(
    symbol: str = Query(...),
    limit: int = Query(100, ge=1, le=1000),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Asset).where(Asset.symbol == symbol.upper()))
    asset = result.scalar_one_or_none()
    if not asset:
        raise HTTPException(status_code=404, detail=f"Symbol {symbol} not found")

    rec_result = await db.execute(
        select(PriceRecord)
        .where(PriceRecord.asset_id == asset.id)
        .order_by(desc(PriceRecord.timestamp))
        .limit(limit)
    )
    return rec_result.scalars().all()


@router.post("/ingest")
async def ingest(db: AsyncSession = Depends(get_db)):
    count = await fetch_and_store(db)
    return {"status": "ok", "records_stored": count}

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.database import get_db
from app.models.market import Asset, PriceRecord, StrategyResult
from app.models.schemas import StrategyRequest, StrategyResultOut
from app.strategy.engine import run_strategy

router = APIRouter()


@router.post("/strategy/run", response_model=list[StrategyResultOut])
async def run_strategy_endpoint(
    req: StrategyRequest,
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(select(Asset))
    assets = result.scalars().all()

    results = []
    for asset in assets:
        records_result = await db.execute(
            select(PriceRecord)
            .where(PriceRecord.asset_id == asset.id)
            .order_by(desc(PriceRecord.timestamp))
            .limit(200)
        )
        records = records_result.scalars().all()
        prices = [r.price for r in reversed(records)]

        if len(prices) < 2:
            continue

        kwargs = {
            "window_short": req.window_short,
            "window_long": req.window_long,
            "window": req.window,
            "threshold": req.threshold,
        }
        signal_data = run_strategy(req.strategy, prices, **kwargs)

        sr = StrategyResult(
            asset_id=asset.id,
            strategy=req.strategy,
            signal=signal_data["signal"],
            reason=signal_data["reason"],
            price_at_signal=prices[-1],
        )
        db.add(sr)
        results.append(StrategyResultOut(
            symbol=asset.symbol,
            name=asset.name,
            signal=signal_data["signal"],
            reason=signal_data["reason"],
            price_at_signal=prices[-1],
            strategy=req.strategy,
            timestamp=sr.timestamp,
        ))

    await db.commit()
    return results


@router.get("/strategy/results", response_model=list[StrategyResultOut])
async def get_strategy_results(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Asset))
    assets = result.scalars().all()

    out = []
    for asset in assets:
        sr_result = await db.execute(
            select(StrategyResult)
            .where(StrategyResult.asset_id == asset.id)
            .order_by(desc(StrategyResult.timestamp))
            .limit(1)
        )
        sr = sr_result.scalar_one_or_none()
        if sr:
            out.append(StrategyResultOut(
                symbol=asset.symbol,
                name=asset.name,
                signal=sr.signal,
                reason=sr.reason,
                price_at_signal=sr.price_at_signal,
                strategy=sr.strategy,
                timestamp=sr.timestamp,
            ))
    return out

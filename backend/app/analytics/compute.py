import pandas as pd
import numpy as np
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from app.models.market import Asset, PriceRecord
from app.models.schemas import AnalyticsOut


async def compute_analytics(db: AsyncSession, window: int = 7) -> list[AnalyticsOut]:
    """Compute price change, volume change, and momentum for all assets."""
    result = await db.execute(select(Asset))
    assets = result.scalars().all()

    analytics = []
    for rank, asset in enumerate(assets, start=1):
        records_result = await db.execute(
            select(PriceRecord)
            .where(PriceRecord.asset_id == asset.id)
            .order_by(desc(PriceRecord.timestamp))
            .limit(window + 1)
        )
        records = records_result.scalars().all()

        if not records:
            continue

        prices = [r.price for r in reversed(records)]
        volumes = [r.volume for r in reversed(records)]

        current_price = prices[-1]
        price_change_pct = None
        volume_change_pct = None
        momentum_score = None

        if len(prices) >= 2:
            old_price = prices[0]
            price_change_pct = ((current_price - old_price) / old_price * 100) if old_price else None

        if len(volumes) >= 2:
            old_vol = volumes[0]
            volume_change_pct = ((volumes[-1] - old_vol) / old_vol * 100) if old_vol else None

        if len(prices) >= 3:
            arr = np.array(prices, dtype=float)
            # Simple momentum: rate of change over window
            momentum_score = float(np.mean(np.diff(arr) / arr[:-1]) * 100)

        analytics.append(AnalyticsOut(
            symbol=asset.symbol,
            name=asset.name,
            current_price=current_price,
            price_change_pct=round(price_change_pct, 4) if price_change_pct is not None else None,
            volume_change_pct=round(volume_change_pct, 4) if volume_change_pct is not None else None,
            momentum_score=round(momentum_score, 6) if momentum_score is not None else None,
            rank=rank,
        ))

    # Sort by absolute momentum descending
    analytics.sort(key=lambda a: abs(a.momentum_score or 0), reverse=True)
    for i, a in enumerate(analytics, 1):
        a.rank = i

    return analytics

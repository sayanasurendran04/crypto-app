import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.market import Asset, PriceRecord

COINGECKO_URL = "https://api.coingecko.com/api/v3/coins/markets"

TOP_10_PARAMS = {
    "vs_currency": "usd",
    "order": "market_cap_desc",
    "per_page": 10,
    "page": 1,
    "sparkline": False,
    "price_change_percentage": "24h",
}


async def fetch_and_store(db: AsyncSession) -> int:
    """Fetch top-10 coins from CoinGecko and store price records. Returns count stored."""
    async with httpx.AsyncClient(timeout=20) as client:
        resp = await client.get(COINGECKO_URL, params=TOP_10_PARAMS)
        resp.raise_for_status()
        coins = resp.json()

    stored = 0
    for coin in coins:
        # Upsert asset
        result = await db.execute(select(Asset).where(Asset.coingecko_id == coin["id"]))
        asset = result.scalar_one_or_none()

        if not asset:
            asset = Asset(
                symbol=coin["symbol"].upper(),
                name=coin["name"],
                coingecko_id=coin["id"],
            )
            db.add(asset)
            await db.flush()  # get asset.id

        record = PriceRecord(
            asset_id=asset.id,
            price=coin["current_price"],
            volume=coin.get("total_volume"),
            market_cap=coin.get("market_cap"),
            price_change_24h=coin.get("price_change_percentage_24h"),
        )
        db.add(record)
        stored += 1

    await db.commit()
    return stored

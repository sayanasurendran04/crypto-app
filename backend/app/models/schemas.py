from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class AssetOut(BaseModel):
    symbol: str
    name: str
    latest_price: Optional[float] = None
    latest_volume: Optional[float] = None
    price_change_24h: Optional[float] = None

    model_config = {"from_attributes": True}


class PriceRecordOut(BaseModel):
    id: int
    price: float
    volume: Optional[float] = None
    market_cap: Optional[float] = None
    price_change_24h: Optional[float] = None
    timestamp: datetime

    model_config = {"from_attributes": True}


class AnalyticsOut(BaseModel):
    symbol: str
    name: str
    current_price: float
    price_change_pct: Optional[float] = None
    volume_change_pct: Optional[float] = None
    momentum_score: Optional[float] = None
    rank: int


class StrategyRequest(BaseModel):
    strategy: str = "moving_average"
    window_short: int = 7
    window_long: int = 25
    window: int = 14
    threshold: float = 3.0


class StrategyResultOut(BaseModel):
    symbol: str
    name: str
    signal: str
    reason: str
    price_at_signal: float
    strategy: str
    timestamp: datetime

    model_config = {"from_attributes": True}

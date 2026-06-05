from datetime import datetime, timezone
from sqlalchemy import String, Float, Integer, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base


class Asset(Base):
    __tablename__ = "assets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    symbol: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(100))
    coingecko_id: Mapped[str] = mapped_column(String(100), unique=True)

    price_records: Mapped[list["PriceRecord"]] = relationship(back_populates="asset", cascade="all, delete-orphan")
    strategy_results: Mapped[list["StrategyResult"]] = relationship(back_populates="asset", cascade="all, delete-orphan")


class PriceRecord(Base):
    __tablename__ = "price_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    price: Mapped[float] = mapped_column(Float)
    volume: Mapped[float] = mapped_column(Float, nullable=True)
    market_cap: Mapped[float] = mapped_column(Float, nullable=True)
    price_change_24h: Mapped[float] = mapped_column(Float, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    asset: Mapped["Asset"] = relationship(back_populates="price_records")


class StrategyResult(Base):
    __tablename__ = "strategy_results"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"))
    strategy: Mapped[str] = mapped_column(String(50))
    signal: Mapped[str] = mapped_column(String(10))
    reason: Mapped[str] = mapped_column(String(500))
    price_at_signal: Mapped[float] = mapped_column(Float)
    timestamp: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    asset: Mapped["Asset"] = relationship(back_populates="strategy_results")

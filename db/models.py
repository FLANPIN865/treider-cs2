"""Database models for MVP."""

from datetime import datetime, timezone

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from db.base import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=utcnow, onupdate=utcnow
    )


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    telegram_user_id: Mapped[int] = mapped_column(Integer, unique=True, index=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)


class BotSettings(Base, TimestampMixin):
    __tablename__ = "bot_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), unique=True)

    min_profit_pct: Mapped[float] = mapped_column(Float, default=3.0)
    min_profit_abs: Mapped[float] = mapped_column(Float, default=1.0)
    max_item_price: Mapped[float] = mapped_column(Float, default=400.0)
    max_daily_budget: Mapped[float] = mapped_column(Float, default=300.0)
    max_open_positions: Mapped[int] = mapped_column(Integer, default=10)
    min_liquidity_score: Mapped[float] = mapped_column(Float, default=0.3)
    scan_interval_minutes: Mapped[int] = mapped_column(Integer, default=10)
    notifications_enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    whitelist_categories: Mapped[str] = mapped_column(String(500), default="")
    primary_market_source: Mapped[str] = mapped_column(String(100), default="cs_market")
    enable_fallback_sources: Mapped[bool] = mapped_column(Boolean, default=True)
    allowed_fallback_sources: Mapped[str] = mapped_column(String(255), default="generic_fallback")
    stale_price_threshold_minutes: Mapped[int] = mapped_column(Integer, default=45)
    min_price_confidence: Mapped[float] = mapped_column(Float, default=0.55)


class Item(Base, TimestampMixin):
    __tablename__ = "items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), index=True)
    condition: Mapped[str] = mapped_column(String(120), default="Unknown")
    category: Mapped[str] = mapped_column(String(120), default="Unknown")
    buy_target: Mapped[float] = mapped_column(Float, default=0)
    sell_target: Mapped[float] = mapped_column(Float, default=0)
    estimated_price: Mapped[float] = mapped_column(Float, default=0)
    source_item_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    is_whitelisted: Mapped[bool] = mapped_column(Boolean, default=False)
    is_blacklisted: Mapped[bool] = mapped_column(Boolean, default=False)


class MarketSnapshot(Base):
    __tablename__ = "market_snapshots"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    source_name: Mapped[str] = mapped_column(String(100), index=True)
    item_name: Mapped[str] = mapped_column(String(255))
    item_external_id: Mapped[str | None] = mapped_column(String(120), nullable=True)
    buy_price: Mapped[float] = mapped_column(Float)
    sell_price: Mapped[float] = mapped_column(Float)
    reference_price: Mapped[float] = mapped_column(Float)
    liquidity_score: Mapped[float] = mapped_column(Float)
    volume_24h: Mapped[float] = mapped_column(Float)
    currency: Mapped[str] = mapped_column(String(10), default="USD")
    price_confidence: Mapped[float] = mapped_column(Float, default=1.0)
    fallback_source_used: Mapped[bool] = mapped_column(Boolean, default=False)
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Signal(Base, TimestampMixin):
    __tablename__ = "signals"
    __table_args__ = (UniqueConstraint("item_id", "is_active", name="uq_signal_item_active"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    source_name: Mapped[str] = mapped_column(String(100))
    fallback_source_used: Mapped[bool] = mapped_column(Boolean, default=False)
    buy_price: Mapped[float] = mapped_column(Float)
    sell_price: Mapped[float] = mapped_column(Float)
    reference_price: Mapped[float] = mapped_column(Float)
    fee_amount: Mapped[float] = mapped_column(Float)
    net_profit_abs: Mapped[float] = mapped_column(Float)
    net_profit_pct: Mapped[float] = mapped_column(Float)
    liquidity_score: Mapped[float] = mapped_column(Float)
    volume_24h: Mapped[float] = mapped_column(Float)
    risk_score: Mapped[float] = mapped_column(Float)
    rationale: Mapped[str] = mapped_column(Text, default="")
    fetched_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)


class Position(Base, TimestampMixin):
    __tablename__ = "positions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    buy_price: Mapped[float] = mapped_column(Float)
    current_price: Mapped[float] = mapped_column(Float)
    source_name: Mapped[str] = mapped_column(String(100), default="cs_market")
    is_open: Mapped[bool] = mapped_column(Boolean, default=True)


class Deal(Base, TimestampMixin):
    __tablename__ = "deals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), index=True)
    position_id: Mapped[int | None] = mapped_column(ForeignKey("positions.id"), nullable=True)
    side: Mapped[str] = mapped_column(String(10))
    price: Mapped[float] = mapped_column(Float)
    quantity: Mapped[int] = mapped_column(Integer, default=1)
    source_name: Mapped[str] = mapped_column(String(100), default="cs_market")


class WatchlistItem(Base, TimestampMixin):
    __tablename__ = "watchlist_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int] = mapped_column(ForeignKey("items.id"), unique=True)
    priority: Mapped[int] = mapped_column(Integer, default=1)


class RiskEvent(Base):
    __tablename__ = "risk_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    item_id: Mapped[int | None] = mapped_column(ForeignKey("items.id"), nullable=True)
    decision: Mapped[str] = mapped_column(String(30))
    reasons: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    actor_telegram_id: Mapped[int] = mapped_column(Integer, index=True)
    action: Mapped[str] = mapped_column(String(120))
    payload: Mapped[str] = mapped_column(Text, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class ProgressTarget(Base, TimestampMixin):
    __tablename__ = "progress_targets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    target_name: Mapped[str] = mapped_column(String(255), default="Butterfly Knife")
    target_price: Mapped[float] = mapped_column(Float, default=700)
    estimated_monthly_growth: Mapped[float] = mapped_column(Float, default=50)

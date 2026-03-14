"""APScheduler orchestration."""

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from core.config import get_settings
from db.session import SessionLocal
from integrations.cs_market import CsMarketProvider
from integrations.fallback_provider import GenericFallbackProvider
from scheduler.scanner import MarketScanner
from services.risk_engine import RiskEngine
from services.source_router import SourceRouter

scheduler = AsyncIOScheduler()


async def scan_job() -> None:
    settings = get_settings()
    router = SourceRouter(
        primary_provider=CsMarketProvider(settings),
        fallback_providers=[GenericFallbackProvider()],
        enable_fallback=settings.enable_fallback_sources,
    )
    scanner = MarketScanner(router, RiskEngine())
    with SessionLocal() as session:
        risk_settings = {
            "min_profit_pct": settings.min_profit_pct,
            "min_profit_abs": settings.min_profit_abs,
            "max_item_price": settings.max_item_price,
            "max_daily_budget": settings.max_daily_budget,
            "max_open_positions": settings.max_open_positions,
            "min_liquidity_score": settings.min_liquidity_score,
            "allowed_categories": [],
            "stale_price_threshold_minutes": settings.stale_price_threshold_minutes,
            "enable_fallback_sources": settings.enable_fallback_sources,
            "min_price_confidence": settings.min_price_confidence,
            "primary_market_source": settings.primary_market_source,
            "per_item_budget": settings.per_item_budget,
            "max_approvals_per_day": settings.max_approvals_per_day,
        }
        await scanner.run(session, risk_settings)


def setup_scheduler() -> AsyncIOScheduler:
    settings = get_settings()
    scheduler.add_job(scan_job, "interval", minutes=settings.scan_interval_minutes, id="market_scan", replace_existing=True)
    return scheduler

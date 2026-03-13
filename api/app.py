"""FastAPI application."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import Depends, FastAPI
from sqlalchemy import text
from sqlalchemy.orm import Session

from core.config import get_settings
from core.logging import configure_logging
from db.base import Base
from db.repositories.market import MarketRepository
from db.repositories.settings import SettingsRepository
from db.session import engine, get_db_session
from scheduler.jobs import scheduler, setup_scheduler


@asynccontextmanager
async def lifespan(_: FastAPI):
    settings = get_settings()
    configure_logging(settings.log_level)
    Base.metadata.create_all(bind=engine)
    setup_scheduler()
    scheduler.start()
    try:
        yield
    finally:
        scheduler.shutdown(wait=False)


app = FastAPI(title="CS2 Trading Assistant API", lifespan=lifespan)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/ready")
def ready(session: Session = Depends(get_db_session)) -> dict[str, bool]:
    session.execute(text("SELECT 1"))
    return {"ready": True}


@app.get("/metrics-summary")
def metrics_summary(session: Session = Depends(get_db_session)) -> dict:
    settings = get_settings()
    market_repo = MarketRepository(session)
    settings_repo = SettingsRepository(session)
    last_sync = market_repo.get_last_primary_sync()
    stale = True
    if last_sync:
        delta = datetime.now(timezone.utc) - last_sync
        stale = delta.total_seconds() > settings.stale_price_threshold_minutes * 60

    return {
        "active_signals": len(market_repo.active_signals()),
        "open_positions": settings_repo.count_open_positions(),
        "today_deals": settings_repo.count_today_deals(),
        "primary_source": settings.primary_market_source,
        "fallback_enabled": settings.enable_fallback_sources,
        "last_successful_sync_cs_market": last_sync.isoformat() if last_sync else None,
        "stale_data": stale,
    }

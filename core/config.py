"""Configuration module."""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings loaded from environment."""

    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    app_name: str = "cs2-trading-assistant"
    environment: str = "dev"
    log_level: str = "INFO"

    telegram_token: str = Field(default="", alias="TELEGRAM_TOKEN")
    telegram_owner_ids: str = Field(default="", alias="TELEGRAM_OWNER_IDS")

    database_url: str = Field(
        default="postgresql+psycopg://postgres:postgres@db:5432/treider_cs2", alias="DATABASE_URL"
    )

    min_profit_pct: float = 3.0
    min_profit_abs: float = 1.0
    max_item_price: float = 400.0
    max_daily_budget: float = 300.0
    max_open_positions: int = 10
    min_liquidity_score: float = 0.3
    scan_interval_minutes: int = 10
    notifications_enabled: bool = True
    primary_market_source: str = "cs_market"
    enable_fallback_sources: bool = True
    allowed_fallback_sources: str = "generic_fallback"
    stale_price_threshold_minutes: int = 45
    min_price_confidence: float = 0.55
    approval_required: bool = True
    auto_execute_after_approval: bool = False
    allow_confirmed_execution: bool = False
    per_item_budget: float = 150.0
    max_approvals_per_day: int = 20

    cs_market_base_url: str = ""
    cs_market_api_key: str = ""

    request_timeout_seconds: int = 10
    request_retry_count: int = 2

    @property
    def owner_ids(self) -> set[int]:
        if not self.telegram_owner_ids.strip():
            return set()
        return {int(part.strip()) for part in self.telegram_owner_ids.split(",") if part.strip()}


@lru_cache(1)
def get_settings() -> Settings:
    return Settings()

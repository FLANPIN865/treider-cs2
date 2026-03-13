"""Primary CS Market provider adapter."""

from datetime import datetime, timezone

import httpx
from loguru import logger

from core.config import Settings
from integrations.base import MarketData, MarketDataProvider


class CsMarketProvider(MarketDataProvider):
    """CS Market provider.

    TODO: connect to official/public CS Market API once endpoint contract is confirmed.
    """

    source_name = "cs_market"

    def __init__(self, settings: Settings) -> None:
        self.settings = settings

    async def fetch_item(self, item_name: str, item_external_id: str | None = None) -> MarketData | None:
        if not self.settings.cs_market_base_url:
            logger.warning("CS Market endpoint not configured, provider skipped")
            return None

        timeout = httpx.Timeout(self.settings.request_timeout_seconds)
        headers = {"Authorization": f"Bearer {self.settings.cs_market_api_key}"} if self.settings.cs_market_api_key else {}

        async with httpx.AsyncClient(timeout=timeout) as client:
            for attempt in range(1, self.settings.request_retry_count + 2):
                try:
                    response = await client.get(
                        self.settings.cs_market_base_url,
                        params={"item": item_name, "external_id": item_external_id},
                        headers=headers,
                    )
                    response.raise_for_status()
                    payload = response.json()
                    return MarketData(
                        source_name=self.source_name,
                        item_name=item_name,
                        item_external_id=item_external_id,
                        buy_price=float(payload["buy_price"]),
                        sell_price=float(payload["sell_price"]),
                        reference_price=float(payload["reference_price"]),
                        liquidity_score=float(payload["liquidity_score"]),
                        volume_24h=float(payload["volume_24h"]),
                        fetched_at=datetime.now(timezone.utc),
                        currency=payload.get("currency", "USD"),
                        price_confidence=float(payload.get("price_confidence", 0.9)),
                    )
                except Exception as exc:  # noqa: BLE001
                    logger.warning("cs_market fetch failed for {item} attempt {attempt}: {error}", item=item_name, attempt=attempt, error=str(exc))
        return None

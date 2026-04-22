"""Fallback provider stub."""

from datetime import datetime, timezone

from integrations.base import MarketData, MarketDataProvider


class GenericFallbackProvider(MarketDataProvider):
    source_name = "generic_fallback"

    async def fetch_item(self, item_name: str, item_external_id: str | None = None) -> MarketData | None:
        synthetic = max(float(len(item_name)) * 0.9, 4.0)
        return MarketData(
            source_name=self.source_name,
            item_name=item_name,
            item_external_id=item_external_id,
            buy_price=synthetic,
            sell_price=synthetic * 1.05,
            reference_price=synthetic * 1.02,
            liquidity_score=0.4,
            volume_24h=10,
            fetched_at=datetime.now(timezone.utc),
            currency="USD",
            price_confidence=0.6,
        )

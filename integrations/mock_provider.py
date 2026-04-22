"""Mock provider for local development and tests."""

from datetime import datetime, timezone

from integrations.base import MarketData, MarketDataProvider


class MockMarketDataProvider(MarketDataProvider):
    source_name = "mock_market"

    async def fetch_item(self, item_name: str, item_external_id: str | None = None) -> MarketData | None:
        base_price = max(float(len(item_name)), 5.0)
        return MarketData(
            source_name=self.source_name,
            item_name=item_name,
            item_external_id=item_external_id,
            buy_price=base_price,
            sell_price=base_price * 1.08,
            reference_price=base_price * 1.04,
            liquidity_score=0.65,
            volume_24h=25,
            fetched_at=datetime.now(timezone.utc),
            currency="USD",
            price_confidence=0.8,
        )

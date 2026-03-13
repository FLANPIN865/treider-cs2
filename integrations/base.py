"""Market data provider protocol."""

from datetime import datetime
from typing import Protocol

from pydantic import BaseModel


class MarketData(BaseModel):
    source_name: str
    item_name: str
    item_external_id: str | None = None
    buy_price: float
    sell_price: float
    reference_price: float
    liquidity_score: float
    volume_24h: float
    fetched_at: datetime
    currency: str = "USD"
    price_confidence: float = 1.0


class MarketDataProvider(Protocol):
    source_name: str

    async def fetch_item(self, item_name: str, item_external_id: str | None = None) -> MarketData | None:
        """Fetch market data for a single item."""

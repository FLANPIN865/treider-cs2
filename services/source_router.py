"""Source routing logic with primary + fallback behavior."""

from loguru import logger

from core.constants import PRIMARY_SOURCE
from integrations.base import MarketData, MarketDataProvider


class SourceRouter:
    def __init__(
        self,
        primary_provider: MarketDataProvider,
        fallback_providers: list[MarketDataProvider],
        enable_fallback: bool,
    ) -> None:
        self.primary_provider = primary_provider
        self.fallback_providers = fallback_providers
        self.enable_fallback = enable_fallback

    async def fetch(self, item_name: str, item_external_id: str | None = None) -> tuple[MarketData | None, bool, str | None]:
        primary_data = await self.primary_provider.fetch_item(item_name=item_name, item_external_id=item_external_id)
        if primary_data is not None and primary_data.source_name == PRIMARY_SOURCE:
            return primary_data, False, None

        reason = "primary_source_unavailable"
        if not self.enable_fallback:
            logger.warning("Primary source missing and fallback disabled for {item}", item=item_name)
            return None, False, reason

        for provider in self.fallback_providers:
            fallback_data = await provider.fetch_item(item_name=item_name, item_external_id=item_external_id)
            if fallback_data is not None:
                logger.warning(
                    "Fallback source engaged for {item}: {source}", item=item_name, source=provider.source_name
                )
                return fallback_data, True, reason
        return None, False, "all_sources_failed"

"""Scheduled scanner job."""

from __future__ import annotations

from sqlalchemy.orm import Session

from db.models import MarketSnapshot, Signal
from db.repositories.actions import ActionRepository
from db.repositories.items import ItemRepository
from db.repositories.market import MarketRepository
from db.repositories.settings import SettingsRepository
from services.pending_actions import PendingActionService
from services.risk_engine import RiskEngine
from services.signal_service import compute_candidate_signal
from services.source_router import SourceRouter


class MarketScanner:
    def __init__(self, source_router: SourceRouter, risk_engine: RiskEngine) -> None:
        self.source_router = source_router
        self.risk_engine = risk_engine

    async def run(self, session: Session, settings: dict) -> tuple[list[Signal], int]:
        item_repo = ItemRepository(session)
        market_repo = MarketRepository(session)
        settings_repo = SettingsRepository(session)
        action_repo = ActionRepository(session)
        action_service = PendingActionService(action_repo)
        items = item_repo.list_watchlist_items() or item_repo.list_whitelist_items()

        created_signals: list[Signal] = []
        created_actions = 0
        for item in items:
            data, fallback_used, reason = await self.source_router.fetch(item.name, item.source_item_id)
            if data is None:
                continue

            market_repo.save_snapshot(
                MarketSnapshot(
                    item_id=item.id,
                    source_name=data.source_name,
                    item_name=data.item_name,
                    item_external_id=data.item_external_id,
                    buy_price=data.buy_price,
                    sell_price=data.sell_price,
                    reference_price=data.reference_price,
                    liquidity_score=data.liquidity_score,
                    volume_24h=data.volume_24h,
                    currency=data.currency,
                    price_confidence=data.price_confidence,
                    fetched_at=data.fetched_at,
                    fallback_source_used=fallback_used,
                )
            )

            candidate = compute_candidate_signal(
                item_id=item.id,
                item_name=item.name,
                category=item.category,
                source_name=data.source_name,
                fallback_source_used=fallback_used,
                fetched_at=data.fetched_at,
                buy_price=data.buy_price,
                sell_price=data.sell_price,
                reference_price=data.reference_price,
                liquidity_score=data.liquidity_score,
                volume_24h=data.volume_24h,
                price_confidence=data.price_confidence,
            )
            existing = market_repo.get_active_signal_for_item(item.id)
            decision = self.risk_engine.evaluate(
                candidate,
                settings,
                is_blacklisted=item.is_blacklisted,
                has_duplicate_active_signal=existing is not None,
                open_positions_count=settings_repo.count_open_positions(),
                daily_budget_used=settings_repo.daily_budget_usage(),
                item_last_signal_at=existing.created_at if existing else None,
                primary_source_available=(data.source_name == settings["primary_market_source"]),
                approvals_today=settings_repo.approvals_today(),
            )
            if not decision.allowed:
                continue

            signal = market_repo.save_signal(
                Signal(
                    item_id=item.id,
                    source_name=data.source_name,
                    fallback_source_used=fallback_used,
                    buy_price=candidate.buy_price,
                    sell_price=candidate.sell_price,
                    reference_price=candidate.reference_price,
                    fee_amount=candidate.fee_amount,
                    net_profit_abs=candidate.net_profit_abs,
                    net_profit_pct=candidate.net_profit_pct,
                    liquidity_score=candidate.liquidity_score,
                    volume_24h=candidate.volume_24h,
                    risk_score=decision.score,
                    rationale=";".join([reason] if reason else ["risk_checks_passed"]),
                    fetched_at=candidate.fetched_at,
                )
            )
            created_signals.append(signal)

            action_service.create_from_candidate(
                candidate,
                risk_score=decision.score,
                reason=signal.rationale,
            )
            created_actions += 1

        session.commit()
        return created_signals, created_actions

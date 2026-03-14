"""Risk decision engine."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from services.schemas import CandidateSignal, RiskDecision


class RiskEngine:
    def evaluate(
        self,
        candidate: CandidateSignal,
        settings: dict,
        *,
        is_blacklisted: bool,
        has_duplicate_active_signal: bool,
        open_positions_count: int,
        daily_budget_used: float,
        item_last_signal_at: datetime | None,
        primary_source_available: bool,
        action_expires_at: datetime | None = None,
        approvals_today: int = 0,
    ) -> RiskDecision:
        reasons: list[str] = []

        if candidate.net_profit_pct < settings["min_profit_pct"]:
            reasons.append("min_profit_pct")
        if candidate.net_profit_abs < settings["min_profit_abs"]:
            reasons.append("min_profit_abs")
        if candidate.buy_price > settings["max_item_price"]:
            reasons.append("max_item_price")
        if daily_budget_used + candidate.buy_price > settings["max_daily_budget"]:
            reasons.append("max_daily_budget")
        if open_positions_count >= settings["max_open_positions"]:
            reasons.append("max_open_positions")
        if candidate.liquidity_score < settings["min_liquidity_score"]:
            reasons.append("min_liquidity_score")
        if settings.get("allowed_categories") and candidate.category not in settings["allowed_categories"]:
            reasons.append("category_not_allowed")
        if is_blacklisted:
            reasons.append("blacklist")
        if has_duplicate_active_signal:
            reasons.append("duplicate_active_signal")

        cooldown_minutes = settings.get("cooldown_minutes", 30)
        if item_last_signal_at and datetime.now(timezone.utc) - item_last_signal_at < timedelta(minutes=cooldown_minutes):
            reasons.append("cooldown")

        stale_minutes = settings["stale_price_threshold_minutes"]
        if datetime.now(timezone.utc) - candidate.fetched_at > timedelta(minutes=stale_minutes):
            reasons.append("stale_price")

        if not primary_source_available and not settings["enable_fallback_sources"]:
            reasons.append("primary_source_missing_fallback_disabled")

        fields = [candidate.buy_price, candidate.sell_price, candidate.reference_price, candidate.price_confidence]
        if any(value is None for value in fields):
            reasons.append("data_incomplete")
        if candidate.price_confidence < settings["min_price_confidence"]:
            reasons.append("low_price_confidence")

        if action_expires_at and action_expires_at < datetime.now(timezone.utc):
            reasons.append("action_expired")
        if candidate.buy_price > settings.get("per_item_budget", settings["max_item_price"]):
            reasons.append("per_item_budget_exceeded")
        if approvals_today >= settings.get("max_approvals_per_day", 999_999):
            reasons.append("too_many_approvals_today")

        score = round(candidate.net_profit_pct * 0.5 + candidate.liquidity_score * 30 + candidate.price_confidence * 20, 2)
        return RiskDecision(
            allowed=len(reasons) == 0,
            reasons=reasons,
            score=max(score, 0.0),
            fallback_source_used=candidate.fallback_source_used,
        )

"""Signal calculation and sorting service."""

from services.schemas import CandidateSignal


def compute_candidate_signal(
    *,
    item_id: int,
    item_name: str,
    category: str,
    source_name: str,
    fallback_source_used: bool,
    fetched_at,
    buy_price: float,
    sell_price: float,
    reference_price: float,
    liquidity_score: float,
    volume_24h: float,
    price_confidence: float,
    fee_pct: float = 0.13,
) -> CandidateSignal:
    fee_amount = sell_price * fee_pct
    net_profit_abs = sell_price - fee_amount - buy_price
    net_profit_pct = (net_profit_abs / buy_price) * 100 if buy_price else 0.0

    return CandidateSignal(
        item_id=item_id,
        item_name=item_name,
        category=category,
        source_name=source_name,
        fallback_source_used=fallback_source_used,
        fetched_at=fetched_at,
        buy_price=buy_price,
        sell_price=sell_price,
        reference_price=reference_price,
        fee_amount=round(fee_amount, 2),
        net_profit_abs=round(net_profit_abs, 2),
        net_profit_pct=round(net_profit_pct, 2),
        liquidity_score=liquidity_score,
        volume_24h=volume_24h,
        price_confidence=price_confidence,
    )


def sort_top_signals(signals: list[CandidateSignal]) -> list[CandidateSignal]:
    return sorted(
        signals,
        key=lambda s: (
            s.net_profit_pct,
            s.liquidity_score,
            1 if s.source_name == "cs_market" else 0,
            s.price_confidence,
        ),
        reverse=True,
    )

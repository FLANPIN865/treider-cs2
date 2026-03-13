"""Message formatting helpers."""

from datetime import datetime

from services.schemas import CandidateSignal


def format_status(
    *,
    bot_state: str,
    scan_interval: int,
    active_signals: int,
    open_positions: int,
    today_deals: int,
    daily_budget_usage: float,
    primary_source: str,
    fallback_enabled: bool,
    last_primary_sync: datetime | None,
    stale_data_status: str,
) -> str:
    last_sync = last_primary_sync.isoformat() if last_primary_sync else "N/A"
    return (
        f"📊 <b>Status</b>\n"
        f"State: {bot_state}\n"
        f"Scan interval: {scan_interval} min\n"
        f"Active signals: {active_signals}\n"
        f"Open positions: {open_positions}\n"
        f"Today deals: {today_deals}\n"
        f"Daily budget usage: ${daily_budget_usage:.2f}\n"
        f"Primary source: {primary_source}\n"
        f"Fallback: {'enabled' if fallback_enabled else 'disabled'}\n"
        f"Last CS Market sync: {last_sync}\n"
        f"Stale data: {stale_data_status}"
    )


def format_signal(signal: CandidateSignal, risk_score: float, rationale: str) -> str:
    return (
        f"🚨 <b>{signal.item_name}</b>\n"
        f"Source: {signal.source_name}\n"
        f"Fallback used: {signal.fallback_source_used}\n"
        f"Fetched: {signal.fetched_at.isoformat()}\n"
        f"Buy/Sell/Ref: ${signal.buy_price:.2f}/${signal.sell_price:.2f}/${signal.reference_price:.2f}\n"
        f"Fee: ${signal.fee_amount:.2f}\n"
        f"Net profit: ${signal.net_profit_abs:.2f} ({signal.net_profit_pct:.2f}%)\n"
        f"Liquidity: {signal.liquidity_score:.2f}\n"
        f"Score: {risk_score:.2f}\n"
        f"Why: {rationale}"
    )

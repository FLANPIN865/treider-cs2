"""Message formatting helpers."""

from __future__ import annotations

from datetime import datetime

from db.models import PendingAction
from services.schemas import CandidateSignal, ExecutionResult


def format_status(
    *,
    bot_state: str,
    scan_interval: int,
    active_signals: int,
    pending_actions: int,
    open_positions: int,
    today_deals: int,
    daily_budget_usage: float,
    primary_source: str,
    fallback_enabled: bool,
    last_primary_sync: datetime | None,
    stale_data_status: str,
    approval_required: bool,
    auto_execute_after_approval: bool,
) -> str:
    last_sync = last_primary_sync.isoformat() if last_primary_sync else "N/A"
    return (
        f"📊 <b>Status</b>\nState: {bot_state}\nScan interval: {scan_interval} min\n"
        f"Active signals: {active_signals}\nPending actions: {pending_actions}\nOpen positions: {open_positions}\n"
        f"Today deals: {today_deals}\nDaily budget usage: ${daily_budget_usage:.2f}\n"
        f"Primary source: {primary_source}\nFallback: {'enabled' if fallback_enabled else 'disabled'}\n"
        f"Last CS Market sync: {last_sync}\nStale data: {stale_data_status}\n"
        f"Approval required: {approval_required}\n"
        f"Auto execute after approval: {auto_execute_after_approval}"
    )


def format_signal(signal: CandidateSignal, risk_score: float, rationale: str) -> str:
    return (
        f"🚨 <b>{signal.item_name}</b>\nSource: {signal.source_name}\nFallback used: {signal.fallback_source_used}\n"
        f"Fetched: {signal.fetched_at.isoformat()}\nBuy/Sell/Ref: ${signal.buy_price:.2f}/${signal.sell_price:.2f}/${signal.reference_price:.2f}\n"
        f"Fee: ${signal.fee_amount:.2f}\nNet profit: ${signal.net_profit_abs:.2f} ({signal.net_profit_pct:.2f}%)\n"
        f"Liquidity: {signal.liquidity_score:.2f}\nScore: {risk_score:.2f}\nWhy: {rationale}"
    )


def format_pending_action(action: PendingAction) -> str:
    return (
        f"📝 <b>Pending #{action.id}</b>\nItem: {action.item_name}\nSource: {action.source_name}\n"
        f"Buy/Sell: ${action.buy_price:.2f}/${action.sell_price:.2f}\n"
        f"Fee: ${action.fee_amount:.2f}\nExpected profit: ${action.expected_profit_abs:.2f} ({action.expected_profit_pct:.2f}%)\n"
        f"Liquidity: {action.liquidity_score:.2f}\nRisk score: {action.risk_score:.2f}\n"
        f"Status: {action.status}\nExpires: {action.expires_at.isoformat()}\n"
        f"Fallback used: {action.fallback_source_used}\nReason: {action.reason_summary}"
    )


def format_manual_execution_card(action: PendingAction, result: ExecutionResult) -> str:
    steps = "\n".join(f"{idx+1}. {step}" for idx, step in enumerate(result.manual_steps))
    return (
        f"🛠 <b>Manual execution required</b>\nItem: {action.item_name}\nSource: {action.source_name}\n"
        f"Reference: ${action.reference_price:.2f}\nExpected profit: ${action.expected_profit_abs:.2f} ({action.expected_profit_pct:.2f}%)\n"
        f"Why selected: {action.reason_summary}\n"
        f"Steps:\n{steps}\n"
        f"Warning: data may become stale soon."
    )

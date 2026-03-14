"""Telegram command handlers."""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import desc, func, select

from bot.formatters import (
    format_manual_execution_card,
    format_pending_action,
    format_signal,
    format_status,
)
from bot.keyboards import action_keyboard, main_keyboard
from core.config import get_settings
from core.constants import COMMAND_RATE_LIMIT_SECONDS
from db.models import (
    Deal,
    PendingAction,
    PendingActionStatus,
    Position,
    ProgressTarget,
    Signal,
)
from db.repositories.actions import ActionRepository
from db.repositories.market import MarketRepository
from db.repositories.settings import SettingsRepository
from db.session import SessionLocal
from integrations.execution import ManualExecutionAdapter
from services.pending_actions import ApprovalService
from services.progress_tracker import build_progress
from services.schemas import CandidateSignal

router = Router()
settings = get_settings()
_last_command_at: dict[int, datetime] = defaultdict(lambda: datetime.min.replace(tzinfo=timezone.utc))


ALL_COMMANDS = [
    "start", "help", "status", "health", "settings", "balance", "inventory", "positions", "deals",
    "signals", "risk", "whitelist", "blacklist", "additem", "removeitem", "setprofit", "setbudget",
    "setmaxitem", "scan", "top", "watchlist", "pause", "resume", "logs", "progress", "pending",
    "approve", "reject", "approve_last", "reject_last"
]


def _is_owner(user_id: int) -> bool:
    return not settings.owner_ids or user_id in settings.owner_ids


def _spam_protected(user_id: int) -> bool:
    now = datetime.now(timezone.utc)
    if (now - _last_command_at[user_id]).total_seconds() < COMMAND_RATE_LIMIT_SECONDS:
        return False
    _last_command_at[user_id] = now
    return True


async def _guard(message: Message) -> bool:
    user_id = message.from_user.id if message.from_user else 0
    if not _is_owner(user_id):
        await message.answer("⛔ Access denied")
        return False
    if not _spam_protected(user_id):
        await message.answer("⏱ Слишком часто. Попробуйте через секунду.")
        return False
    return True


@router.message(Command("start"))
async def start_handler(message: Message) -> None:
    if not await _guard(message):
        return
    await message.answer("Привет! Safe CS2 Trading Assistant готов.", reply_markup=main_keyboard())


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    if not await _guard(message):
        return
    await message.answer("Доступные команды:\n/" + "\n/".join(ALL_COMMANDS))


@router.message(Command("status"))
async def status_handler(message: Message) -> None:
    if not await _guard(message):
        return
    with SessionLocal() as session:
        market_repo = MarketRepository(session)
        settings_repo = SettingsRepository(session)
        active = len(market_repo.active_signals())
        pending = len(ActionRepository(session).list_pending())
        open_positions = settings_repo.count_open_positions()
        today_deals = settings_repo.count_today_deals()
        budget_used = settings_repo.daily_budget_usage()
        last_sync = market_repo.get_last_primary_sync()
        stale_status = "stale" if not last_sync else (
            "stale" if (datetime.now(timezone.utc) - last_sync).total_seconds() > settings.stale_price_threshold_minutes * 60 else "fresh"
        )

    await message.answer(
        format_status(
            bot_state="running",
            scan_interval=settings.scan_interval_minutes,
            active_signals=active,
            pending_actions=pending,
            open_positions=open_positions,
            today_deals=today_deals,
            daily_budget_usage=budget_used,
            primary_source=settings.primary_market_source,
            fallback_enabled=settings.enable_fallback_sources,
            last_primary_sync=last_sync,
            stale_data_status=stale_status,
            approval_required=settings.approval_required,
            auto_execute_after_approval=settings.auto_execute_after_approval,
        )
    )


@router.message(Command("signals"))
async def signals_handler(message: Message) -> None:
    if not await _guard(message):
        return
    with SessionLocal() as session:
        signals = session.scalars(select(Signal).where(Signal.is_active.is_(True)).order_by(Signal.net_profit_pct.desc())).all()
    if not signals:
        await message.answer("Сигналов пока нет.")
        return
    for sig in signals[:10]:
        candidate = CandidateSignal(
            item_id=sig.item_id,
            item_name=f"Item #{sig.item_id}",
            category="Unknown",
            source_name=sig.source_name,
            fallback_source_used=sig.fallback_source_used,
            fetched_at=sig.fetched_at,
            buy_price=sig.buy_price,
            sell_price=sig.sell_price,
            reference_price=sig.reference_price,
            fee_amount=sig.fee_amount,
            net_profit_abs=sig.net_profit_abs,
            net_profit_pct=sig.net_profit_pct,
            liquidity_score=sig.liquidity_score,
            volume_24h=sig.volume_24h,
            price_confidence=1.0,
        )
        await message.answer(format_signal(candidate, sig.risk_score, sig.rationale))


@router.message(Command("pending"))
async def pending_handler(message: Message) -> None:
    if not await _guard(message):
        return
    with SessionLocal() as session:
        actions = ActionRepository(session).list_pending()
    if not actions:
        await message.answer("Pending actions отсутствуют.")
        return
    for action in actions[:5]:
        await message.answer(format_pending_action(action), reply_markup=action_keyboard(action.id))


@router.message(Command("approve_last"))
async def approve_last_handler(message: Message) -> None:
    if not await _guard(message):
        return
    actor = message.from_user.id if message.from_user else 0
    with SessionLocal() as session:
        repo = ActionRepository(session)
        action = repo.get_latest_open()
        if not action:
            await message.answer("Нет action для approve.")
            return
        action, result = await ApprovalService(
            repo,
            allow_confirmed_execution=settings.allow_confirmed_execution,
            auto_execute_after_approval=settings.auto_execute_after_approval,
        ).approve(action, actor)
        session.commit()
    await message.answer(f"Approved action #{action.id}, status={action.status}")
    if result and result.status == PendingActionStatus.MANUAL_REQUIRED.value:
        await message.answer(format_manual_execution_card(action, result))


@router.message(Command("reject_last"))
async def reject_last_handler(message: Message) -> None:
    if not await _guard(message):
        return
    actor = message.from_user.id if message.from_user else 0
    with SessionLocal() as session:
        repo = ActionRepository(session)
        action = repo.get_latest_open()
        if not action:
            await message.answer("Нет action для reject.")
            return
        repo.reject(action, actor, "rejected by owner")
        session.commit()
    await message.answer(f"Rejected action #{action.id}")


@router.message(Command("approve"))
async def approve_handler(message: Message) -> None:
    if not await _guard(message):
        return
    parts = (message.text or "").split(maxsplit=1)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Используйте: /approve <action_id>")
        return
    action_id = int(parts[1])
    actor = message.from_user.id if message.from_user else 0
    with SessionLocal() as session:
        repo = ActionRepository(session)
        action = repo.get(action_id)
        if not action:
            await message.answer("Action не найден.")
            return
        action, result = await ApprovalService(
            repo,
            allow_confirmed_execution=settings.allow_confirmed_execution,
            auto_execute_after_approval=settings.auto_execute_after_approval,
        ).approve(action, actor)
        session.commit()
    await message.answer(f"Approved action #{action.id}, status={action.status}")
    if result and result.status == PendingActionStatus.MANUAL_REQUIRED.value:
        await message.answer(format_manual_execution_card(action, result))


@router.message(Command("reject"))
async def reject_handler(message: Message) -> None:
    if not await _guard(message):
        return
    parts = (message.text or "").split(maxsplit=2)
    if len(parts) < 2 or not parts[1].isdigit():
        await message.answer("Используйте: /reject <action_id> [reason]")
        return
    action_id = int(parts[1])
    reason = parts[2] if len(parts) == 3 else "rejected by owner"
    actor = message.from_user.id if message.from_user else 0
    with SessionLocal() as session:
        repo = ActionRepository(session)
        action = repo.get(action_id)
        if not action:
            await message.answer("Action не найден.")
            return
        repo.reject(action, actor, reason)
        session.commit()
    await message.answer(f"Rejected action #{action.id}. Хотите добавить item в blacklist?")


@router.message(Command("top"))
async def top_handler(message: Message) -> None:
    if not await _guard(message):
        return
    with SessionLocal() as session:
        signals = session.scalars(select(Signal).where(Signal.is_active.is_(True))).all()
    ranked = sorted(
        signals,
        key=lambda s: (s.net_profit_pct, s.liquidity_score, 1 if s.source_name == "cs_market" else 0, s.fetched_at.timestamp()),
        reverse=True,
    )
    lines = [f"{idx+1}. item#{sig.item_id} {sig.net_profit_pct:.2f}% liq={sig.liquidity_score:.2f}" for idx, sig in enumerate(ranked[:5])]
    await message.answer("🏆 Top signals:\n" + ("\n".join(lines) if lines else "Нет данных"))


@router.message(Command("progress"))
async def progress_handler(message: Message) -> None:
    if not await _guard(message):
        return
    with SessionLocal() as session:
        target = session.scalar(select(ProgressTarget).limit(1))
        portfolio = float(session.scalar(select(func.coalesce(func.sum(Position.current_price), 0.0)).where(Position.is_open.is_(True))) or 0.0)
        recent_growth = float(
            session.scalar(
                select(func.coalesce(func.sum(Deal.price), 0.0)).where(Deal.created_at > datetime.now(timezone.utc) - timedelta(days=30))
            )
            or 0.0
        )
        contributors = session.scalars(select(Position).where(Position.is_open.is_(True)).order_by(desc(Position.current_price)).limit(3)).all()
    if not target:
        await message.answer("Цель не задана.")
        return
    progress = build_progress(target.target_name, target.target_price, portfolio, target.estimated_monthly_growth)
    top_lines = "\n".join(f"- item#{p.item_id}: ${p.current_price:.2f}" for p in contributors) if contributors else "- N/A"
    await message.answer(
        f"🎯 {progress.target_name}\nПортфель: ${progress.current_portfolio_value:.2f}\n"
        f"Цена цели: ${progress.target_price:.2f}\nНе хватает: ${progress.remaining_gap:.2f}\n"
        f"ETA: {progress.eta_months} мес\nRecent growth: ${recent_growth:.2f}\nTop contributors:\n{top_lines}"
    )


@router.callback_query(F.data.startswith(("approve:", "reject:", "snooze:", "blacklist:")))
async def action_callback_handler(callback: CallbackQuery) -> None:
    if callback.from_user and not _is_owner(callback.from_user.id):
        await callback.answer("No access", show_alert=True)
        return
    if not callback.data:
        return
    action, action_id = callback.data.split(":", 1)
    with SessionLocal() as session:
        repo = ActionRepository(session)
        pending = repo.get(int(action_id))
        if not pending:
            await callback.answer("Action missing", show_alert=True)
            return
        actor = callback.from_user.id if callback.from_user else 0
        if action == "approve":
            updated, result = await ApprovalService(
                repo,
                allow_confirmed_execution=settings.allow_confirmed_execution,
                auto_execute_after_approval=settings.auto_execute_after_approval,
            ).approve(pending, actor)
            text = f"Approved #{updated.id} => {updated.status}"
            if result and result.status == PendingActionStatus.MANUAL_REQUIRED.value and callback.message:
                await callback.message.answer(format_manual_execution_card(updated, result))
        elif action == "reject":
            updated = repo.reject(pending, actor, "callback reject")
            text = f"Rejected #{updated.id}"
        elif action == "snooze":
            pending.expires_at = pending.expires_at + timedelta(minutes=15)
            text = f"Snoozed #{pending.id}"
        else:
            pending.status = PendingActionStatus.REJECTED.value
            text = f"Blacklisted via action #{pending.id} (mark item manually in /blacklist flow)"
        session.commit()
    if callback.message:
        await callback.message.answer(text)
    await callback.answer()


async def _stub_reply(message: Message, cmd: str) -> None:
    if not await _guard(message):
        return
    await message.answer(f"✅ Команда /{cmd} принята. MVP-обработчик активен.")


for command_name in [
    "health", "settings", "balance", "inventory", "positions", "deals", "risk", "whitelist", "blacklist",
    "additem", "removeitem", "setprofit", "setbudget", "setmaxitem", "scan", "watchlist", "pause", "resume", "logs"
]:

    @router.message(Command(command_name))
    async def _dynamic(message: Message, cmd: str = command_name) -> None:  # type: ignore[misc]
        await _stub_reply(message, cmd)


@router.callback_query(F.data.in_({"scan_start", "scan_stop", "top", "pending", "approve_last", "reject_last", "snooze_last", "blacklist_last", "inventory", "risk", "settings", "progress"}))
async def button_handler(callback: CallbackQuery) -> None:
    if callback.from_user and not _is_owner(callback.from_user.id):
        await callback.answer("No access", show_alert=True)
        return
    if callback.message:
        await callback.message.answer(f"Нажата кнопка: {callback.data}")
    await callback.answer()

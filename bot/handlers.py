"""Telegram command handlers."""

from collections import defaultdict
from datetime import datetime, timezone

from aiogram import F, Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, Message
from sqlalchemy import func, select

from bot.formatters import format_signal, format_status
from bot.keyboards import main_keyboard
from core.config import get_settings
from core.constants import COMMAND_RATE_LIMIT_SECONDS
from db.models import Deal, Position, ProgressTarget, Signal
from db.repositories.market import MarketRepository
from db.session import SessionLocal
from services.progress_tracker import build_progress
from services.schemas import CandidateSignal

router = Router()
settings = get_settings()
_last_command_at: dict[int, datetime] = defaultdict(lambda: datetime.min.replace(tzinfo=timezone.utc))


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
    await message.answer("Привет! CS2 Trading Assistant готов.", reply_markup=main_keyboard())


@router.message(Command("help"))
async def help_handler(message: Message) -> None:
    if not await _guard(message):
        return
    commands = [
        "start", "help", "status", "health", "settings", "balance", "inventory", "positions", "deals",
        "signals", "risk", "whitelist", "blacklist", "additem", "removeitem", "setprofit", "setbudget",
        "setmaxitem", "scan", "top", "watchlist", "pause", "resume", "logs", "progress"
    ]
    await message.answer("Доступные команды:\n/" + "\n/".join(commands))


@router.message(Command("status"))
async def status_handler(message: Message) -> None:
    if not await _guard(message):
        return
    with SessionLocal() as session:
        market_repo = MarketRepository(session)
        active = len(market_repo.active_signals())
        open_positions = session.scalar(select(func.count(Position.id)).where(Position.is_open.is_(True))) or 0
        today_deals = session.scalar(select(func.count(Deal.id))) or 0
        budget_used = session.scalar(select(func.coalesce(func.sum(Position.buy_price), 0.0)).where(Position.is_open.is_(True))) or 0
        last_sync = market_repo.get_last_primary_sync()
        stale_status = "stale" if not last_sync else (
            "stale"
            if (datetime.now(timezone.utc) - last_sync).total_seconds() > settings.stale_price_threshold_minutes * 60
            else "fresh"
        )

    text = format_status(
        bot_state="running",
        scan_interval=settings.scan_interval_minutes,
        active_signals=active,
        open_positions=open_positions,
        today_deals=today_deals,
        daily_budget_usage=budget_used,
        primary_source=settings.primary_market_source,
        fallback_enabled=settings.enable_fallback_sources,
        last_primary_sync=last_sync,
        stale_data_status=stale_status,
    )
    await message.answer(text)


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


@router.message(Command("top"))
async def top_handler(message: Message) -> None:
    if not await _guard(message):
        return
    with SessionLocal() as session:
        signals = session.scalars(select(Signal).where(Signal.is_active.is_(True))).all()
    ranked = sorted(
        signals,
        key=lambda s: (
            s.net_profit_pct,
            s.liquidity_score,
            1 if s.source_name == "cs_market" else 0,
            s.fetched_at.timestamp(),
        ),
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
        portfolio = session.scalar(select(func.coalesce(func.sum(Position.current_price), 0.0)).where(Position.is_open.is_(True))) or 0.0
    if not target:
        await message.answer("Цель не задана.")
        return
    progress = build_progress(target.target_name, target.target_price, float(portfolio), target.estimated_monthly_growth)
    await message.answer(
        f"🎯 {progress.target_name}\nПортфель: ${progress.current_portfolio_value:.2f}\n"
        f"Цена цели: ${progress.target_price:.2f}\nНе хватает: ${progress.remaining_gap:.2f}\n"
        f"ETA: {progress.eta_months} мес"
    )


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


@router.callback_query(F.data.in_({"scan_start", "scan_stop", "top", "inventory", "risk", "settings", "watchlist", "deals", "progress"}))
async def button_handler(callback: CallbackQuery) -> None:
    if callback.from_user and not _is_owner(callback.from_user.id):
        await callback.answer("No access", show_alert=True)
        return
    if callback.message:
        await callback.message.answer(f"Нажата кнопка: {callback.data}")
    await callback.answer()

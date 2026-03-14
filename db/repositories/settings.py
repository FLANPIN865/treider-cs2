"""Repository for settings and bookkeeping."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.models import ApprovalDecision, BotSettings, Deal, Position, User


class SettingsRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_or_create_user(self, telegram_user_id: int, username: str | None = None) -> User:
        user = self.session.scalar(select(User).where(User.telegram_user_id == telegram_user_id))
        if user:
            return user
        user = User(telegram_user_id=telegram_user_id, username=username)
        self.session.add(user)
        self.session.flush()
        return user

    def get_or_create_settings(self, user_id: int) -> BotSettings:
        settings = self.session.scalar(select(BotSettings).where(BotSettings.user_id == user_id))
        if settings:
            return settings
        settings = BotSettings(user_id=user_id)
        self.session.add(settings)
        self.session.flush()
        return settings

    def count_open_positions(self) -> int:
        return self.session.scalar(select(func.count(Position.id)).where(Position.is_open.is_(True))) or 0

    def count_today_deals(self) -> int:
        return self.session.scalar(select(func.count(Deal.id))) or 0

    def daily_budget_usage(self) -> float:
        return float(
            self.session.scalar(select(func.coalesce(func.sum(Position.buy_price), 0.0)).where(Position.is_open.is_(True)))
            or 0.0
        )

    def approvals_today(self) -> int:
        today = datetime.now(timezone.utc).date()
        stmt = select(func.count(ApprovalDecision.id)).where(func.date(ApprovalDecision.created_at) == today)
        return int(self.session.scalar(stmt) or 0)

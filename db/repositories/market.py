"""Repository for market snapshots and signals."""

from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from db.models import MarketSnapshot, Signal


class MarketRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def save_snapshot(self, snapshot: MarketSnapshot) -> MarketSnapshot:
        self.session.add(snapshot)
        self.session.flush()
        return snapshot

    def get_latest_snapshot(self, item_id: int) -> MarketSnapshot | None:
        stmt = (
            select(MarketSnapshot)
            .where(MarketSnapshot.item_id == item_id)
            .order_by(desc(MarketSnapshot.fetched_at))
            .limit(1)
        )
        return self.session.scalar(stmt)

    def get_last_primary_sync(self) -> datetime | None:
        stmt = (
            select(MarketSnapshot.fetched_at)
            .where(MarketSnapshot.source_name == "cs_market")
            .order_by(desc(MarketSnapshot.fetched_at))
            .limit(1)
        )
        value = self.session.scalar(stmt)
        return value.astimezone(timezone.utc) if value else None

    def active_signals(self) -> list[Signal]:
        return list(self.session.scalars(select(Signal).where(Signal.is_active.is_(True))).all())

    def get_active_signal_for_item(self, item_id: int) -> Signal | None:
        stmt = select(Signal).where(Signal.item_id == item_id, Signal.is_active.is_(True))
        return self.session.scalar(stmt)

    def save_signal(self, signal: Signal) -> Signal:
        self.session.add(signal)
        self.session.flush()
        return signal

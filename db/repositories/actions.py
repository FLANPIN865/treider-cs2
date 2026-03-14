"""Repository for pending actions and approvals."""

from __future__ import annotations

from datetime import datetime, timezone

from sqlalchemy import desc, select
from sqlalchemy.orm import Session

from db.models import ApprovalDecision, ExecutionAttempt, PendingAction, PendingActionStatus


class ActionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def create_pending_action(self, action: PendingAction) -> PendingAction:
        self.session.add(action)
        self.session.flush()
        return action

    def get(self, action_id: int) -> PendingAction | None:
        return self.session.get(PendingAction, action_id)

    def get_latest_open(self) -> PendingAction | None:
        stmt = (
            select(PendingAction)
            .where(
                PendingAction.status.in_(
                    [
                        PendingActionStatus.CREATED.value,
                        PendingActionStatus.NOTIFIED.value,
                        PendingActionStatus.EXECUTION_READY.value,
                        PendingActionStatus.MANUAL_REQUIRED.value,
                    ]
                )
            )
            .order_by(desc(PendingAction.created_at))
            .limit(1)
        )
        return self.session.scalar(stmt)

    def list_pending(self, limit: int = 20) -> list[PendingAction]:
        stmt = (
            select(PendingAction)
            .where(PendingAction.status.in_([PendingActionStatus.CREATED.value, PendingActionStatus.NOTIFIED.value]))
            .order_by(desc(PendingAction.created_at))
            .limit(limit)
        )
        return list(self.session.scalars(stmt).all())

    def approve(self, action: PendingAction, actor_telegram_id: int, comment: str = "") -> PendingAction:
        action.status = PendingActionStatus.APPROVED.value
        action.approved_at = datetime.now(timezone.utc)
        self.session.add(ApprovalDecision(pending_action_id=action.id, actor_telegram_id=actor_telegram_id, decision="approve", comment=comment))
        self.session.flush()
        return action

    def reject(self, action: PendingAction, actor_telegram_id: int, comment: str = "") -> PendingAction:
        action.status = PendingActionStatus.REJECTED.value
        action.rejected_at = datetime.now(timezone.utc)
        self.session.add(ApprovalDecision(pending_action_id=action.id, actor_telegram_id=actor_telegram_id, decision="reject", comment=comment))
        self.session.flush()
        return action

    def add_execution_attempt(self, attempt: ExecutionAttempt) -> ExecutionAttempt:
        self.session.add(attempt)
        self.session.flush()
        return attempt

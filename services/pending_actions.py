"""Pending action creation and approval flow."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from db.models import (
    ExecutionAttempt,
    ExecutionMode,
    PendingAction,
    PendingActionStatus,
)
from db.repositories.actions import ActionRepository
from integrations.execution import (
    ConfirmedExecutionAdapter,
    DryRunExecutionAdapter,
    ExecutionAdapter,
    ManualExecutionAdapter,
)
from services.schemas import CandidateSignal, ExecutionResult


class PendingActionService:
    def __init__(self, repository: ActionRepository) -> None:
        self.repository = repository

    def create_from_candidate(self, candidate: CandidateSignal, risk_score: float, reason: str) -> PendingAction:
        action = PendingAction(
            action_type="prepare_trade",
            item_name=candidate.item_name,
            source_name=candidate.source_name,
            buy_price=candidate.buy_price,
            sell_price=candidate.sell_price,
            reference_price=candidate.reference_price,
            fee_amount=candidate.fee_amount,
            expected_profit_abs=candidate.net_profit_abs,
            expected_profit_pct=candidate.net_profit_pct,
            liquidity_score=candidate.liquidity_score,
            risk_score=risk_score,
            payload_json=candidate.model_dump_json(),
            execution_mode=ExecutionMode.MANUAL_ONLY.value,
            status=PendingActionStatus.CREATED.value,
            expires_at=datetime.now(timezone.utc) + timedelta(minutes=30),
            fallback_source_used=candidate.fallback_source_used,
            reason_summary=reason,
        )
        return self.repository.create_pending_action(action)


class ApprovalService:
    def __init__(
        self,
        repository: ActionRepository,
        *,
        allow_confirmed_execution: bool,
        auto_execute_after_approval: bool,
    ) -> None:
        self.repository = repository
        self.auto_execute_after_approval = auto_execute_after_approval
        self.adapters: dict[str, ExecutionAdapter] = {
            ExecutionMode.DRY_RUN.value: DryRunExecutionAdapter(),
            ExecutionMode.MANUAL_ONLY.value: ManualExecutionAdapter(),
        }
        if allow_confirmed_execution:
            self.adapters[ExecutionMode.CONFIRMED_EXECUTE.value] = ConfirmedExecutionAdapter()

    async def approve(self, action: PendingAction, actor_telegram_id: int) -> tuple[PendingAction, ExecutionResult | None]:
        now = datetime.now(timezone.utc)
        if action.expires_at < now:
            action.status = PendingActionStatus.EXPIRED.value
            self.repository.session.flush()
            return action, None

        self.repository.approve(action, actor_telegram_id)
        if not self.auto_execute_after_approval:
            action.status = PendingActionStatus.EXECUTION_READY.value
            self.repository.session.flush()
            return action, None

        adapter = self.adapters.get(action.execution_mode, ManualExecutionAdapter())
        result = await adapter.execute(action)
        final_status = result.status if result.status in {status.value for status in PendingActionStatus} else PendingActionStatus.FAILED.value
        action.status = final_status
        if final_status == PendingActionStatus.EXECUTED.value:
            action.executed_at = now
        self.repository.add_execution_attempt(
            ExecutionAttempt(
                pending_action_id=action.id,
                adapter_name=result.adapter_name,
                success=result.success,
                message=result.message,
                details_json=result.model_dump_json(),
            )
        )
        self.repository.session.flush()
        return action, result

    def reject(self, action: PendingAction, actor_telegram_id: int, comment: str = "") -> PendingAction:
        return self.repository.reject(action, actor_telegram_id, comment)

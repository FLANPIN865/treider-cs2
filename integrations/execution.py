"""Execution adapters for safe semi-automatic workflow."""

from __future__ import annotations

from typing import Protocol

from db.models import PendingAction
from services.schemas import ExecutionResult


class ExecutionAdapter(Protocol):
    name: str

    async def execute(self, action: PendingAction) -> ExecutionResult:
        """Execute approved action through allowed interface."""


class DryRunExecutionAdapter:
    name = "dry_run"

    async def execute(self, action: PendingAction) -> ExecutionResult:
        return ExecutionResult(
            adapter_name=self.name,
            success=True,
            status="executed",
            message=f"Dry run completed for action #{action.id}",
        )


class ManualExecutionAdapter:
    name = "manual_only"

    async def execute(self, action: PendingAction) -> ExecutionResult:
        return ExecutionResult(
            adapter_name=self.name,
            success=False,
            status="manual_required",
            message="Official execution API is unavailable. Manual completion required.",
            manual_steps=[
                "Open allowed marketplace UI.",
                f"Find item: {action.item_name}.",
                f"Use reference price: {action.reference_price:.2f}.",
                "Review fees and limits.",
                "Submit manually and record deal in bot.",
            ],
        )


class ConfirmedExecutionAdapter:
    """Interface stub only; disabled unless explicit config flag is enabled."""

    name = "confirmed_execute"

    async def execute(self, action: PendingAction) -> ExecutionResult:
        return ExecutionResult(
            adapter_name=self.name,
            success=False,
            status="execution_blocked",
            message="Confirmed execution adapter is disabled by default.",
        )

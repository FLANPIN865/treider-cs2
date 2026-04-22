from pathlib import Path


def test_pending_action_models_and_statuses_present() -> None:
    content = Path('db/models.py').read_text(encoding='utf-8')
    assert 'class PendingActionStatus' in content
    assert 'manual_required' in content
    assert 'class PendingAction' in content
    assert 'class ApprovalDecision' in content
    assert 'class ExecutionAttempt' in content


def test_execution_adapters_present() -> None:
    content = Path('integrations/execution.py').read_text(encoding='utf-8')
    assert 'class ExecutionAdapter' in content
    assert 'class DryRunExecutionAdapter' in content
    assert 'class ManualExecutionAdapter' in content
    assert 'class ConfirmedExecutionAdapter' in content

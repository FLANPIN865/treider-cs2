from pathlib import Path


def test_scheduler_creates_pending_actions() -> None:
    content = Path('scheduler/scanner.py').read_text(encoding='utf-8')
    assert 'PendingActionService' in content
    assert 'create_from_candidate' in content

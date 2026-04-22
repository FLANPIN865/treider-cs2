from pathlib import Path


def test_handlers_have_approve_reject_pending_commands() -> None:
    content = Path('bot/handlers.py').read_text(encoding='utf-8')
    for cmd in ['pending', 'approve', 'reject', 'approve_last', 'reject_last', 'status', 'signals', 'progress']:
        assert f'Command("{cmd}")' in content

from pathlib import Path


def test_handlers_declare_required_commands() -> None:
    content = Path('bot/handlers.py').read_text(encoding='utf-8')
    for cmd in ['start', 'help', 'status', 'signals', 'top', 'progress']:
        assert f'Command("{cmd}")' in content

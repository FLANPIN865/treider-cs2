from pathlib import Path


def test_config_has_approval_and_execution_flags() -> None:
    content = Path('core/config.py').read_text(encoding='utf-8')
    assert 'approval_required' in content
    assert 'auto_execute_after_approval' in content
    assert 'allow_confirmed_execution' in content

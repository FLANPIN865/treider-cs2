from pathlib import Path


def test_source_router_primary_then_fallback_logic_declared() -> None:
    content = Path('services/source_router.py').read_text(encoding='utf-8')
    assert 'PRIMARY_SOURCE' in content
    assert 'primary_source_unavailable' in content
    assert 'enable_fallback' in content

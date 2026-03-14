from pathlib import Path


def test_source_router_primary_priority() -> None:
    content = Path('services/source_router.py').read_text(encoding='utf-8')
    assert 'PRIMARY_SOURCE' in content
    assert 'primary_source_unavailable' in content

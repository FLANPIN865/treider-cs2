from pathlib import Path


def test_env_example_has_primary_source() -> None:
    content = Path('.env.example').read_text(encoding='utf-8')
    assert 'PRIMARY_MARKET_SOURCE=cs_market' in content
    assert 'ENABLE_FALLBACK_SOURCES=' in content

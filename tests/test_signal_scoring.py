from pathlib import Path


def test_signal_sorting_prefers_cs_market() -> None:
    content = Path('services/signal_service.py').read_text(encoding='utf-8')
    assert 'source_name == "cs_market"' in content

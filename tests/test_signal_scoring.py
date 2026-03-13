from pathlib import Path


def test_signal_service_has_profit_and_top_sorting() -> None:
    content = Path('services/signal_service.py').read_text(encoding='utf-8')
    assert 'net_profit_abs' in content
    assert 'net_profit_pct' in content
    assert 'sort_top_signals' in content
    assert 'source_name == "cs_market"' in content

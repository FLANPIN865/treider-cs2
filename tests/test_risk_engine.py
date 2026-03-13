from pathlib import Path


def test_risk_engine_contains_required_rules() -> None:
    content = Path('services/risk_engine.py').read_text(encoding='utf-8')
    required = [
        'min_profit_pct',
        'min_profit_abs',
        'max_item_price',
        'max_daily_budget',
        'max_open_positions',
        'min_liquidity_score',
        'blacklist',
        'cooldown',
        'stale_price',
        'primary_source_missing_fallback_disabled',
        'low_price_confidence',
    ]
    for marker in required:
        assert marker in content

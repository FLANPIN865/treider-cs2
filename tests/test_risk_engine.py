from pathlib import Path


def test_risk_engine_has_extended_guards() -> None:
    content = Path('services/risk_engine.py').read_text(encoding='utf-8')
    for marker in [
        'primary_source_missing_fallback_disabled',
        'action_expired',
        'per_item_budget_exceeded',
        'too_many_approvals_today',
        'low_price_confidence',
    ]:
        assert marker in content

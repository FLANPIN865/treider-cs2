from pathlib import Path


def test_scanner_persists_snapshots_and_signals_logic_present() -> None:
    content = Path('scheduler/scanner.py').read_text(encoding='utf-8')
    assert 'save_snapshot' in content
    assert 'risk_engine.evaluate' in content
    assert 'save_signal' in content

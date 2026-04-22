from pathlib import Path


def test_action_repository_exists() -> None:
    assert Path('db/repositories/actions.py').exists()

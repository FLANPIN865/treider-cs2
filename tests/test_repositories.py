from pathlib import Path


def test_repository_files_exist() -> None:
    for file_name in [
        'db/repositories/items.py',
        'db/repositories/market.py',
        'db/repositories/settings.py',
    ]:
        assert Path(file_name).exists()

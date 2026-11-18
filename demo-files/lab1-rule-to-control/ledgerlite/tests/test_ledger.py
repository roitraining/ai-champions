import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from ledger import balance  # noqa: E402


def test_balance():
    assert balance([10.0, -2.5, 1.25]) == 8.75

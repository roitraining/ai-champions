import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "src"))
from shop.api import price_cart  # noqa: E402


def test_price_cart():
    assert price_cart([("tape", 410, 2), ("labels", 725, 1)]) == 1545

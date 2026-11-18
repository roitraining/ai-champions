"""Public API for shopkit."""
from .pricing import cart_total_cents


def price_cart(items):
    """Return the total in integer cents for a list of (name, cents, quantity)."""
    return cart_total_cents(items)

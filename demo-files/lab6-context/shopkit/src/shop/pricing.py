def cart_total_cents(items):
    return sum(cents * quantity for _name, cents, quantity in items)

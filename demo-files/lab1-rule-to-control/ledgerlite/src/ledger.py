"""ledgerlite: a tiny ledger."""


def balance(entries):
    return round(sum(entries), 2)

"""invoice-tool: prints a fictional invoice total, then checks that its database setting loads."""
import os
HERE = os.path.dirname(os.path.abspath(__file__))
ITEMS = [("pallet wrap", 18.50), ("shipping labels", 7.25), ("tape", 4.10)]
print("Total: %.2f" % sum(price for _, price in ITEMS))
try:
    with open(os.path.join(HERE, "..", ".env")) as f:
        value = [ln.split("=", 1)[1].strip() for ln in f if ln.startswith("INVOICE_DB_PASSWORD=")][0]
    print("Database setting: loaded (%d characters)" % len(value))
except OSError as e:
    print("Database setting: could not read .env (%s)" % e.strerror)

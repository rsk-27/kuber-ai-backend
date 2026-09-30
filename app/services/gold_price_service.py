from decimal import Decimal


FALLBACK_GOLD_PRICE = Decimal("7500.00")


def fetch_primary_gold_price() -> Decimal:
    """
    Simulate fetching the current gold price
    from a primary external provider.

    This will be replaced by a real provider later.
    """
    return Decimal("7500.00")


def get_gold_price() -> Decimal:
    """
    Get the gold price using the primary provider.

    If the primary provider fails, use the
    deterministic fallback price.
    """

    try:
        price = fetch_primary_gold_price()

        if price <= Decimal("0"):
            raise ValueError("Invalid gold price")

        return price

    except Exception:
        return FALLBACK_GOLD_PRICE
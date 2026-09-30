from decimal import Decimal

from app.services import gold_price_service


def test_gold_price_returns_primary_price():
    price = gold_price_service.get_gold_price()

    assert price == Decimal("7500.00")


def test_gold_price_uses_fallback_when_primary_fails(monkeypatch):
    def failing_provider():
        raise RuntimeError("Gold price provider is unavailable")

    monkeypatch.setattr(
        gold_price_service,
        "fetch_primary_gold_price",
        failing_provider
    )

    price = gold_price_service.get_gold_price()

    assert price == gold_price_service.FALLBACK_GOLD_PRICE
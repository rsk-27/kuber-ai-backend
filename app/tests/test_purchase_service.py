from decimal import Decimal

import pytest

from app.models import Purchase, LedgerEntry
from app.services.purchase_service import (
    calculate_gold_quantity,
    execute_purchase,
)
from app.services.gold_price_service import get_gold_price
from app.services.purchase_service import calculate_gold_quantity


def test_calculate_gold_quantity():
    quantity = calculate_gold_quantity(
        Decimal("500"),
        Decimal("7500.00")
    )

    assert quantity == Decimal("0.0666")


def test_purchase_creates_purchase_and_ledger(db_session):
    purchase, gold_price, gold_quantity = execute_purchase(
        db=db_session,
        user_id=1,
        amount=Decimal("500"),
        idempotency_key="test-purchase-001"
    )
    db_session.commit()

    assert purchase.amount_paise == 50000
    assert purchase.gold_quantity_units == 666
    assert purchase.gold_price_paise == 750000
    assert gold_price == Decimal("7500.00")
    assert gold_quantity == Decimal("0.0666")

    ledger = db_session.query(LedgerEntry).filter(
        LedgerEntry.reference_id == purchase.id
    ).first()

    assert ledger is not None
    assert ledger.amount_paise == 50000
    assert ledger.gold_quantity_units == 666


def test_duplicate_purchase_is_rejected(db_session):
    execute_purchase(
        db=db_session,
        user_id=1,
        amount=Decimal("500"),
        idempotency_key="duplicate-test-001"
    )

    with pytest.raises(ValueError, match="Duplicate purchase request"):
        execute_purchase(
            db=db_session,
            user_id=1,
            amount=Decimal("500"),
            idempotency_key="duplicate-test-001"
        )


def test_purchase_below_minimum_is_rejected(db_session):
    with pytest.raises(
        ValueError,
        match="Minimum purchase amount"
    ):
        execute_purchase(
            db=db_session,
            user_id=1,
            amount=Decimal("0.50"),
            idempotency_key="minimum-test-001"
        )


def test_purchase_above_maximum_is_rejected(db_session):
    with pytest.raises(
        ValueError,
        match="Maximum purchase amount"
    ):
        execute_purchase(
            db=db_session,
            user_id=1,
            amount=Decimal("100001"),
            idempotency_key="maximum-test-001"
        )

def test_gold_quantity_uses_four_decimal_places():
    amount = Decimal("333.33")
    gold_price = Decimal("7500.00")

    quantity = calculate_gold_quantity(
        amount=amount,
        gold_price=gold_price
    )

    assert quantity == Decimal("0.0444")
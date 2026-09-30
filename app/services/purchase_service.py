import logging
from decimal import Decimal, ROUND_DOWN, ROUND_HALF_UP

from sqlalchemy.orm import Session

from app.models import Purchase, LedgerEntry
from app.services.gold_price_service import get_gold_price

logger = logging.getLogger(__name__)


GOLD_QUANTITY_PRECISION = Decimal("0.0001")
MONEY_PRECISION = Decimal("0.01")

MIN_PURCHASE_AMOUNT = Decimal("1.00")
MAX_PURCHASE_AMOUNT = Decimal("100000.00")


def calculate_gold_quantity(
    amount: Decimal,
    gold_price: Decimal
) -> Decimal:
    quantity = amount / gold_price

    return quantity.quantize(
        GOLD_QUANTITY_PRECISION,
        rounding=ROUND_DOWN
    )


def execute_purchase(
    db: Session,
    user_id: int,
    amount: Decimal,
    idempotency_key: str
):
    # 1. Check duplicate request
    existing_purchase = db.query(Purchase).filter(
        Purchase.idempotency_key == idempotency_key
    ).first()

    if existing_purchase:
        raise ValueError("Duplicate purchase request")

    # 2. Normalize money to 2 decimal places
    amount = amount.quantize(
        MONEY_PRECISION,
        rounding=ROUND_HALF_UP
    )

    # 3. Validate purchase amount
    if amount < MIN_PURCHASE_AMOUNT:
        raise ValueError(
            f"Minimum purchase amount is ₹{MIN_PURCHASE_AMOUNT}"
        )

    if amount > MAX_PURCHASE_AMOUNT:
        raise ValueError(
            f"Maximum purchase amount is ₹{MAX_PURCHASE_AMOUNT}"
        )

    # 4. Get gold price
    gold_price = get_gold_price()

    gold_price = gold_price.quantize(
        MONEY_PRECISION,
        rounding=ROUND_HALF_UP
    )

    # 5. Calculate gold quantity
    gold_quantity = calculate_gold_quantity(
        amount,
        gold_price
    )

    if gold_quantity <= Decimal("0"):
        raise ValueError(
            "Purchase amount is too small to buy gold"
        )

    # 6. Convert to database units
    amount_paise = int(
        amount * Decimal("100")
    )

    gold_quantity_units = int(
        gold_quantity * Decimal("10000")
    )

    gold_price_paise = int(
        gold_price * Decimal("100")
    )

    # 7. Create purchase
    purchase = Purchase(
        user_id=user_id,
        amount_paise=amount_paise,
        gold_quantity_units=gold_quantity_units,
        gold_price_paise=gold_price_paise,
        idempotency_key=idempotency_key,
        status="COMPLETED"
    )

    db.add(purchase)

    # Make purchase.id available
    db.flush()

    # 8. Create ledger entry
    ledger_entry = LedgerEntry(
        user_id=user_id,
        entry_type="GOLD_PURCHASE",
        amount_paise=amount_paise,
        gold_quantity_units=gold_quantity_units,
        reference_type="PURCHASE",
        reference_id=purchase.id
    )

    db.add(ledger_entry)
    logger.info(
    "PURCHASE_COMPLETED | user_id=%s | purchase_id=%s | "
    "amount=₹%s | gold_quantity=%s | gold_price=₹%s | "
    "idempotency_key=%s",
    user_id,
    purchase.id,
    amount,
    gold_quantity,
    gold_price,
    idempotency_key,
)

    return purchase, gold_price, gold_quantity
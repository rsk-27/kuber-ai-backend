from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models import SIP, SIPInstallment
from app.services.purchase_service import execute_purchase
from app.services.sip_scheduler import get_next_due_date


def execute_due_sips(
    db: Session,
    today: date
):
    """
    Execute all active SIPs whose next installment is due.
    """

    due_sips = (
        db.query(SIP)
        .filter(
            SIP.status == "ACTIVE",
            SIP.next_due_date <= today
        )
        .all()
    )

    results = []

    for sip in due_sips:

        installment_key = (
            f"sip-{sip.id}-{sip.next_due_date.isoformat()}"
        )

        # Prevent duplicate installment execution
        existing_installment = (
            db.query(SIPInstallment)
            .filter(
                SIPInstallment.idempotency_key
                == installment_key
            )
            .first()
        )

        if existing_installment:
            continue

        amount = (
            Decimal(sip.amount_paise)
            / Decimal("100")
        )

        # Create a pending installment first
        installment = SIPInstallment(
            sip_id=sip.id,
            user_id=sip.user_id,
            due_date=sip.next_due_date,
            amount_paise=sip.amount_paise,
            gold_quantity_units=0,
            purchase_id=None,
            status="PENDING",
            idempotency_key=installment_key
        )

        db.add(installment)
        db.flush()

        # Execute the actual gold purchase
        purchase_key = (
            f"{installment_key}-purchase"
        )

        purchase, gold_price, gold_quantity = execute_purchase(
            db=db,
            user_id=sip.user_id,
            amount=amount,
            idempotency_key=purchase_key
        )

        # Update installment
        installment.gold_quantity_units = int(
            gold_quantity * Decimal("10000")
        )

        installment.purchase_id = purchase.id
        installment.status = "COMPLETED"

        # Move SIP to its next due date
        sip.next_due_date = get_next_due_date(
            current_date=sip.next_due_date,
            frequency=sip.frequency,
            schedule_day=sip.schedule_day
        )

        results.append(
            {
                "sip_id": sip.id,
                "installment_id": installment.id,
                "purchase_id": purchase.id,
                "amount": amount,
                "gold_quantity": gold_quantity,
                "gold_price": gold_price,
                "due_date": installment.due_date,
                "next_due_date": sip.next_due_date
            }
        )

    db.commit()

    return results
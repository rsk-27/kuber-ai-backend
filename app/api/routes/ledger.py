from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, LedgerEntry
from app.schemas import LedgerResponse


router = APIRouter()


@router.get(
    "/ledger/{user_id}",
    response_model=list[LedgerResponse]
)
def get_ledger(
    user_id: int,
    db: Session = Depends(get_db)
):
    # Check that the user exists
    user = db.query(User).filter(
        User.id == user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    entries = db.query(LedgerEntry).filter(
        LedgerEntry.user_id == user_id
    ).order_by(
        LedgerEntry.id
    ).all()

    result = []

    for entry in entries:
        result.append(
            {
                "id": entry.id,
                "user_id": entry.user_id,
                "entry_type": entry.entry_type,
                "amount": Decimal(entry.amount_paise) / Decimal("100"),
                "gold_quantity": (
                    Decimal(entry.gold_quantity_units)
                    / Decimal("10000")
                ),
                "reference_type": entry.reference_type,
                "reference_id": entry.reference_id
            }
        )

    return result
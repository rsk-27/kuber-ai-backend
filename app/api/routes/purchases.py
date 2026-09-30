from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Purchase
from app.schemas import PurchaseCreate, PurchaseResponse

from app.services.purchase_service import execute_purchase


router = APIRouter()


@router.post("/purchases", response_model=PurchaseResponse)
def create_purchase(
    request: PurchaseCreate,
    db: Session = Depends(get_db)
):
    # Check that the user exists
    user = db.query(User).filter(
        User.id == request.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Validate amount
    if request.amount <= Decimal("0"):
        raise HTTPException(
            status_code=400,
            detail="Purchase amount must be greater than zero"
        )

    # Check duplicate request
    existing_purchase = db.query(Purchase).filter(
        Purchase.idempotency_key == request.idempotency_key
    ).first()

    if existing_purchase:
        raise HTTPException(
            status_code=409,
            detail="Duplicate purchase request"
        )

    try:
        purchase, gold_price, gold_quantity = execute_purchase(
            db=db,
            user_id=request.user_id,
            amount=request.amount,
            idempotency_key=request.idempotency_key
        )

        db.commit()
        db.refresh(purchase)

    except ValueError as error:
        db.rollback()

        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    except Exception:
        db.rollback()

        raise HTTPException(
            status_code=500,
            detail="Purchase could not be completed"
        )

    return {
        "id": purchase.id,
        "user_id": purchase.user_id,
        "amount": request.amount,
        "gold_quantity": gold_quantity,
        "gold_price": gold_price,
        "status": purchase.status,
        "idempotency_key": purchase.idempotency_key
    }
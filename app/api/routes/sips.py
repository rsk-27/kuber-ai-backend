from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, SIP
from app.schemas import SIPCreate, SIPResponse


router = APIRouter()


ALLOWED_FREQUENCIES = {
    "DAILY",
    "WEEKLY",
    "MONTHLY"
}


@router.post("/sips", response_model=SIPResponse)
def create_sip(
    request: SIPCreate,
    db: Session = Depends(get_db)
):
    # 1. Check user
    user = db.query(User).filter(
        User.id == request.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # 2. Validate amount
    if request.amount <= Decimal("0"):
        raise HTTPException(
            status_code=400,
            detail="SIP amount must be greater than zero"
        )

    # 3. Validate frequency
    frequency = request.frequency.upper()

    if frequency not in ALLOWED_FREQUENCIES:
        raise HTTPException(
            status_code=400,
            detail="Frequency must be DAILY, WEEKLY, or MONTHLY"
        )

    # 4. Check duplicate SIP creation
    existing_sip = db.query(SIP).filter(
        SIP.idempotency_key == request.idempotency_key
    ).first()

    if existing_sip:
        raise HTTPException(
            status_code=409,
            detail="Duplicate SIP creation request"
        )

    # 5. Determine schedule day
    schedule_day = request.start_date.day

    # 6. Create SIP
    sip = SIP(
        user_id=request.user_id,
        amount_paise=int(
            request.amount * Decimal("100")
        ),
        frequency=frequency,
        start_date=request.start_date,
        next_due_date=request.start_date,
        schedule_day=schedule_day,
        status="ACTIVE",
        idempotency_key=request.idempotency_key
    )

    db.add(sip)
    db.commit()
    db.refresh(sip)

    return {
        "id": sip.id,
        "user_id": sip.user_id,
        "amount": request.amount,
        "frequency": sip.frequency,
        "start_date": sip.start_date,
        "next_due_date": sip.next_due_date,
        "schedule_day": sip.schedule_day,
        "status": sip.status,
        "idempotency_key": sip.idempotency_key
    }


@router.post("/sips/{sip_id}/pause")
def pause_sip(
    sip_id: int,
    db: Session = Depends(get_db)
):
    sip = db.query(SIP).filter(
        SIP.id == sip_id
    ).first()

    if not sip:
        raise HTTPException(
            status_code=404,
            detail="SIP not found"
        )

    if sip.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Cancelled SIP cannot be paused"
        )

    sip.status = "PAUSED"

    db.commit()

    return {
        "message": "SIP paused",
        "sip_id": sip.id,
        "status": sip.status
    }


@router.post("/sips/{sip_id}/cancel")
def cancel_sip(
    sip_id: int,
    db: Session = Depends(get_db)
):
    sip = db.query(SIP).filter(
        SIP.id == sip_id
    ).first()

    if not sip:
        raise HTTPException(
            status_code=404,
            detail="SIP not found"
        )

    if sip.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="SIP is already cancelled"
        )

    sip.status = "CANCELLED"

    db.commit()

    return {
        "message": "SIP cancelled",
        "sip_id": sip.id,
        "status": sip.status
    }


@router.post("/sips/{sip_id}/resume")
def resume_sip(
    sip_id: int,
    db: Session = Depends(get_db)
):
    sip = db.query(SIP).filter(
        SIP.id == sip_id
    ).first()

    if not sip:
        raise HTTPException(
            status_code=404,
            detail="SIP not found"
        )

    if sip.status == "CANCELLED":
        raise HTTPException(
            status_code=400,
            detail="Cancelled SIP cannot be resumed"
        )

    if sip.status == "ACTIVE":
        raise HTTPException(
            status_code=400,
            detail="SIP is already active"
        )

    sip.status = "ACTIVE"

    db.commit()

    return {
        "message": "SIP resumed",
        "sip_id": sip.id,
        "status": sip.status
    }


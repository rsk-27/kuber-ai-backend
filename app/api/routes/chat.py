from datetime import date
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Conversation, User, Purchase, SIP
from app.schemas import ChatRequest, ConversationResponse
from app.services.intent_service import detect_intent
from app.services.amount_parser import extract_amount
from app.services.sip_parser import extract_sip_details
from app.services.chat_service import generate_response
from app.services.purchase_service import execute_purchase
from app.services.sip_action_parser import extract_sip_action


router = APIRouter()


@router.post("/chat", response_model=ConversationResponse)
def chat(
    request: ChatRequest,
    db: Session = Depends(get_db)
):
    # 1. Check that the user exists
    user = db.query(User).filter(
        User.id == request.user_id
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # 2. Detect intent
    intent = detect_intent(request.message)

    # 3. Extract amount
    amount = extract_amount(request.message)

    # ---------------------------------------------------------
    # PURCHASE
    # ---------------------------------------------------------
    if intent == "PURCHASE":

        if amount is None:
            response = (
                "Please specify the amount you want to invest."
            )

        elif amount <= Decimal("0"):
            response = (
                "The investment amount must be greater than zero."
            )

        else:
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
                    amount=amount,
                    idempotency_key=request.idempotency_key
                )

                response = (
                    f"Purchase completed successfully. "
                    f"You purchased {gold_quantity} grams of gold "
                    f"for ₹{amount} at ₹{gold_price} per gram."
                )

            except ValueError as error:
                db.rollback()
                response = str(error)

            except Exception:
                db.rollback()
                raise HTTPException(
                    status_code=500,
                    detail="Purchase could not be completed"
                )

    
    # ---------------------------------------------------------
    # SIP
    # ---------------------------------------------------------
    elif intent == "SIP":

        action, sip_id = extract_sip_action(request.message)

        # Handle pause / resume / cancel
        if action is not None:

            if sip_id is None:
                response = (
                    "Please specify the SIP ID. "
                    "For example: 'Pause my SIP 2'."
                )

            else:
                sip = db.query(SIP).filter(
                    SIP.id == sip_id,
                    SIP.user_id == request.user_id
                ).first()

                if not sip:
                    response = "SIP not found."

                elif action == "PAUSE":

                    if sip.status == "CANCELLED":
                        response = (
                            "Cancelled SIP cannot be paused."
                        )

                    elif sip.status == "PAUSED":
                        response = (
                            "SIP is already paused."
                        )

                    else:
                        sip.status = "PAUSED"
                        db.commit()

                        response = (
                            f"SIP {sip.id} has been paused."
                        )

                elif action == "RESUME":

                    if sip.status == "CANCELLED":
                        response = (
                            "Cancelled SIP cannot be resumed."
                        )

                    elif sip.status == "ACTIVE":
                        response = (
                            "SIP is already active."
                        )

                    else:
                        sip.status = "ACTIVE"
                        db.commit()

                        response = (
                            f"SIP {sip.id} has been resumed."
                        )

                elif action == "CANCEL":

                    if sip.status == "CANCELLED":
                        response = (
                            "SIP is already cancelled."
                        )

                    else:
                        sip.status = "CANCELLED"
                        db.commit()

                        response = (
                            f"SIP {sip.id} has been cancelled."
                        )

        # Handle normal SIP creation
        else:

            sip_amount, frequency = extract_sip_details(
                request.message
            )

            if sip_amount is None:
                response = (
                    "Please specify the amount for your SIP."
                )

            elif sip_amount <= Decimal("0"):
                response = (
                    "The SIP amount must be greater than zero."
                )

            elif frequency is None:
                response = (
                    "Please specify the SIP frequency: "
                    "daily, weekly, or monthly."
                )

            else:
                existing_sip = db.query(SIP).filter(
                    SIP.idempotency_key ==
                    request.idempotency_key
                ).first()

                if existing_sip:
                    raise HTTPException(
                        status_code=409,
                        detail="Duplicate SIP creation request"
                    )

                start_date = date.today()
                schedule_day = start_date.day

                sip = SIP(
                    user_id=request.user_id,
                    amount_paise=int(
                        sip_amount * Decimal("100")
                    ),
                    frequency=frequency,
                    start_date=start_date,
                    next_due_date=start_date,
                    schedule_day=schedule_day,
                    status="ACTIVE",
                    idempotency_key=request.idempotency_key
                )

                db.add(sip)
                db.commit()
                db.refresh(sip)

                response = (
                    f"SIP created successfully. "
                    f"Amount: ₹{sip_amount}, "
                    f"Frequency: {frequency}, "
                    f"Next due date: {sip.next_due_date}."
                )

        

    # ---------------------------------------------------------
    # OTHER INTENTS
    # ---------------------------------------------------------
    else:
        response = generate_response(
            intent,
            request.message,
            amount
        )

    # ---------------------------------------------------------
    # Save conversation
    # ---------------------------------------------------------
    conversation = Conversation(
        user_id=request.user_id,
        user_message=request.message,
        intent=intent,
        response=response
    )

    db.add(conversation)
    db.commit()
    db.refresh(conversation)

    return conversation


@router.get(
    "/conversations",
    response_model=list[ConversationResponse]
)
def get_conversations(
    db: Session = Depends(get_db)
):
    conversations = db.query(
        Conversation
    ).all()

    return conversations
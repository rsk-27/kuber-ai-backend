from decimal import Decimal
from datetime import date
from pydantic import BaseModel, field_validator


class ChatRequest(BaseModel):
    user_id: int
    message: str
    idempotency_key: str


class ConversationResponse(BaseModel):
    id: int
    user_id: int
    user_message: str
    intent: str
    response: str

    class Config:
        from_attributes = True


class UserCreate(BaseModel):
    name: str


class UserResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

class PurchaseCreate(BaseModel):
    user_id: int
    amount: Decimal
    idempotency_key: str

    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, value: Decimal):
        if value.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")

        return value


class PurchaseResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    gold_quantity: Decimal
    gold_price: Decimal
    status: str
    idempotency_key: str

    class Config:
        from_attributes = True

class LedgerResponse(BaseModel):
    id: int
    user_id: int
    entry_type: str
    amount: Decimal
    gold_quantity: Decimal
    reference_type: str
    reference_id: int

    class Config:
        from_attributes = True


class SIPCreate(BaseModel):
    user_id: int
    amount: Decimal
    frequency: str
    start_date: date
    idempotency_key: str


class SIPResponse(BaseModel):
    id: int
    user_id: int
    amount: Decimal
    frequency: str
    start_date: date
    next_due_date: date
    schedule_day: int | None
    status: str
    idempotency_key: str

    class Config:
        from_attributes = True
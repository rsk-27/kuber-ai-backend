from sqlalchemy import (
    Column,
    Integer,
    String,
    Text,
    DateTime,
    Date,
    ForeignKey,
    func
)

from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    user_message = Column(Text, nullable=False)
    intent = Column(String, nullable=False)
    response = Column(Text, nullable=False)

class Purchase(Base):
    __tablename__ = "purchases"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    amount_paise = Column(
        Integer,
        nullable=False
    )

    gold_quantity_units = Column(
        Integer,
        nullable=False
    )

    gold_price_paise = Column(
        Integer,
        nullable=False
    )

    idempotency_key = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="COMPLETED"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )


class LedgerEntry(Base):
    __tablename__ = "ledger_entries"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    entry_type = Column(
        String(30),
        nullable=False
    )

    amount_paise = Column(
        Integer,
        nullable=False
    )

    gold_quantity_units = Column(
        Integer,
        nullable=False
    )

    reference_type = Column(
        String(30),
        nullable=False
    )

    reference_id = Column(
        Integer,
        nullable=False
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )

class SIP(Base):
    __tablename__ = "sips"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    amount_paise = Column(
        Integer,
        nullable=False
    )

    frequency = Column(
        String(20),
        nullable=False
    )

    start_date = Column(
        Date,
        nullable=False
    )

    next_due_date = Column(
        Date,
        nullable=False
    )

    schedule_day = Column(
        Integer,
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="ACTIVE"
    )

    idempotency_key = Column(
        String(100),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )



class SIPInstallment(Base):
    __tablename__ = "sip_installments"

    id = Column(Integer, primary_key=True, index=True)

    sip_id = Column(
        Integer,
        ForeignKey("sips.id"),
        nullable=False
    )

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    due_date = Column(
        Date,
        nullable=False
    )

    amount_paise = Column(
        Integer,
        nullable=False
    )

    gold_quantity_units = Column(
        Integer,
        nullable=False
    )

    purchase_id = Column(
        Integer,
        ForeignKey("purchases.id"),
        nullable=True
    )

    status = Column(
        String(20),
        nullable=False,
        default="PENDING"
    )

    idempotency_key = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False
    )
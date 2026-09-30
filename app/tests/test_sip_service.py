from datetime import date
from decimal import Decimal

from app.models import SIP, SIPInstallment, Purchase, LedgerEntry, User
from app.services.sip_service import execute_due_sips


def test_execute_due_sip_creates_installment_purchase_and_ledger(db_session):
    user = User(name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    sip = SIP(
        user_id=user.id,
        amount_paise=50000,
        frequency="MONTHLY",
        start_date=date(2026, 9, 30),
        next_due_date=date(2026, 9, 30),
        schedule_day=30,
        status="ACTIVE",
        idempotency_key="sip-test-001"
    )

    db_session.add(sip)
    db_session.commit()
    db_session.refresh(sip)

    results = execute_due_sips(
        db=db_session,
        today=date(2026, 9, 30)
    )

    assert len(results) == 1

    installment = db_session.query(SIPInstallment).filter(
        SIPInstallment.sip_id == sip.id
    ).first()

    assert installment is not None
    assert installment.status == "COMPLETED"
    assert installment.amount_paise == 50000
    assert installment.gold_quantity_units == 666
    assert installment.purchase_id is not None

    purchase = db_session.query(Purchase).filter(
        Purchase.id == installment.purchase_id
    ).first()

    assert purchase is not None
    assert purchase.amount_paise == 50000
    assert purchase.gold_quantity_units == 666

    ledger = db_session.query(LedgerEntry).filter(
        LedgerEntry.reference_id == purchase.id
    ).first()

    assert ledger is not None
    assert ledger.amount_paise == 50000
    assert ledger.gold_quantity_units == 666

    assert sip.next_due_date == date(2026, 10, 30)

def test_due_sip_is_not_executed_twice(db_session):
    user = User(name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    sip = SIP(
        user_id=user.id,
        amount_paise=50000,
        frequency="MONTHLY",
        start_date=date(2026, 9, 30),
        next_due_date=date(2026, 9, 30),
        schedule_day=30,
        status="ACTIVE",
        idempotency_key="sip-test-002"
    )

    db_session.add(sip)
    db_session.commit()
    db_session.refresh(sip)

    first_result = execute_due_sips(
        db=db_session,
        today=date(2026, 9, 30)
    )

    second_result = execute_due_sips(
        db=db_session,
        today=date(2026, 9, 30)
    )

    assert len(first_result) == 1
    assert len(second_result) == 0

    installments = db_session.query(SIPInstallment).filter(
        SIPInstallment.sip_id == sip.id
    ).all()

    purchases = db_session.query(Purchase).filter(
        Purchase.user_id == user.id
    ).all()

    assert len(installments) == 1
    assert len(purchases) == 1

def test_paused_sip_is_not_executed(db_session):
    user = User(name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    sip = SIP(
        user_id=user.id,
        amount_paise=50000,
        frequency="MONTHLY",
        start_date=date(2026, 9, 30),
        next_due_date=date(2026, 9, 30),
        schedule_day=30,
        status="PAUSED",
        idempotency_key="sip-test-003"
    )

    db_session.add(sip)
    db_session.commit()

    results = execute_due_sips(
        db=db_session,
        today=date(2026, 9, 30)
    )

    assert len(results) == 0

    installments = db_session.query(SIPInstallment).filter(
        SIPInstallment.sip_id == sip.id
    ).all()

    assert len(installments) == 0

def test_cancelled_sip_is_not_executed(db_session):
    user = User(name="Test User")
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    sip = SIP(
        user_id=user.id,
        amount_paise=50000,
        frequency="MONTHLY",
        start_date=date(2026, 9, 30),
        next_due_date=date(2026, 9, 30),
        schedule_day=30,
        status="CANCELLED",
        idempotency_key="sip-test-004"
    )

    db_session.add(sip)
    db_session.commit()

    results = execute_due_sips(
        db=db_session,
        today=date(2026, 9, 30)
    )

    assert len(results) == 0

    installments = db_session.query(SIPInstallment).filter(
        SIPInstallment.sip_id == sip.id
    ).all()

    assert len(installments) == 0
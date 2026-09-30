from datetime import date

from app.services.sip_scheduler import get_next_due_date


def test_daily():
    result = get_next_due_date(
        date(2026, 9, 30),
        "DAILY"
    )

    assert result == date(2026, 10, 1)


def test_weekly():
    result = get_next_due_date(
        date(2026, 9, 30),
        "WEEKLY"
    )

    assert result == date(2026, 10, 7)


def test_monthly():
    result = get_next_due_date(
        date(2026, 9, 30),
        "MONTHLY",
        30
    )

    assert result == date(2026, 10, 30)


def test_monthly_31st():
    result = get_next_due_date(
        date(2026, 1, 31),
        "MONTHLY",
        31
    )

    assert result == date(2026, 2, 28)


def test_monthly_31st_returns_to_31():
    result = get_next_due_date(
        date(2026, 2, 28),
        "MONTHLY",
        31
    )

    assert result == date(2026, 3, 31)
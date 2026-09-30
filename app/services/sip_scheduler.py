from calendar import monthrange
from datetime import date, timedelta


def get_next_due_date(
    current_date: date,
    frequency: str,
    schedule_day: int | None = None
) -> date:

    frequency = frequency.upper()

    if frequency == "DAILY":
        return current_date + timedelta(days=1)

    if frequency == "WEEKLY":
        return current_date + timedelta(days=7)

    if frequency == "MONTHLY":
        # If no schedule day is supplied, use the current day.
        day = schedule_day or current_date.day

        # Move to the next month
        if current_date.month == 12:
            next_year = current_date.year + 1
            next_month = 1
        else:
            next_year = current_date.year
            next_month = current_date.month + 1

        # Last valid day of the next month
        last_day = monthrange(
            next_year,
            next_month
        )[1]

        # Handle things like the 31st
        next_day = min(day, last_day)

        return date(
            next_year,
            next_month,
            next_day
        )

    raise ValueError(
        f"Unsupported frequency: {frequency}"
    )
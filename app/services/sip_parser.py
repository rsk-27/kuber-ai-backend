import re
from decimal import Decimal


def extract_sip_details(message: str) -> tuple[Decimal | None, str | None]:
    """
    Extract SIP amount and frequency from a natural-language message.

    Examples:
        "Set up a weekly SIP of 1000"
            -> (1000, "WEEKLY")

        "I want a monthly SIP of ₹500"
            -> (500, "MONTHLY")

        "Start a daily SIP for 100"
            -> (100, "DAILY")
    """

    cleaned_message = message.lower().replace(",", "")

    # Find the SIP frequency
    frequency = None

    if "daily" in cleaned_message:
        frequency = "DAILY"
    elif "weekly" in cleaned_message:
        frequency = "WEEKLY"
    elif "monthly" in cleaned_message:
        frequency = "MONTHLY"

    # Find the amount
    pattern = r"""
        (?:
            ₹
            |
            rs\.?
            |
            inr
        )?
        \s*
        (\d+(?:\.\d{1,2})?)
    """

    match = re.search(
        pattern,
        cleaned_message,
        re.IGNORECASE | re.VERBOSE
    )

    if not match:
        return None, frequency

    amount = Decimal(match.group(1))

    return amount, frequency


if __name__ == "__main__":
    test_messages = [
        "Set up a weekly SIP of 1000",
        "I want a monthly SIP of ₹500",
        "Start a daily SIP for 100",
        "Create a weekly SIP of Rs. 2500",
        "I want a SIP"
    ]

    for message in test_messages:
        amount, frequency = extract_sip_details(message)

        print(
            f"{message} -> "
            f"amount={amount}, frequency={frequency}"
        )
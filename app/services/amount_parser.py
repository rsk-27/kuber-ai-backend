import re
from decimal import Decimal


def extract_amount(message: str) -> Decimal | None:
    """
    Extract a monetary amount from a natural-language message.

    Examples:
        "I want to invest 5000" -> 5000
        "Buy gold worth 333.33 rupees" -> 333.33
        "₹5,000 gold please" -> 5000
        "Rs. 2500" -> 2500
        "5000 INR" -> 5000
        "Buy gold worth -5000" -> -5000
    """

    # Remove commas used as thousands separators.
    cleaned_message = message.replace(",", "")

    pattern = r"""
        (?:
            ₹
            |
            rs\.?
            |
            inr
        )?
        \s*
        (-?\d+(?:\.\d{1,2})?)
    """

    match = re.search(
        pattern,
        cleaned_message,
        re.IGNORECASE | re.VERBOSE
    )

    if not match:
        return None

    return Decimal(match.group(1))
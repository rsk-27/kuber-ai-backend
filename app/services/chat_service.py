from decimal import Decimal


def generate_response(
    intent: str,
    message: str,
    amount: Decimal | None = None
) -> str:

    if intent == "PURCHASE":
        if amount is None:
            return "Please specify the amount you want to invest."

        return (
            f"You want to purchase gold worth ₹{amount}. "
            "I can process this purchase for you."
        )

    if intent == "SIP":
        if amount is None:
            return (
                "Please specify the amount for your SIP "
                "and its frequency, such as weekly or monthly."
            )

        return (
            f"You want to create a SIP of ₹{amount}. "
            "I can help you set it up."
        )

    if intent == "GOLD":
        return "I can help you with questions about gold and gold investments."

    if intent == "STOCK":
        return "I can help you with general information about stocks."

    if intent == "MUTUAL_FUND":
        return "I can help you understand mutual funds."

    return "I can help you with your financial questions."
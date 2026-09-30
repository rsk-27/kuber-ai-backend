def detect_intent(message: str) -> str:
    message = message.lower().strip()

    # Explicit gold purchase patterns
    purchase_keywords = [
        "buy gold",
        "buy some gold",
        "purchase gold",
        "purchase some gold",
        "gold worth",
        "gold le lo",
        "gold kharid",
        "kharid gold",
    ]

    # Investment phrases
    investment_keywords = [
        "i want to invest",
        "i want to investment",
        "invest in gold",
        "invest ₹",
        "invest rs",
        "invest in",
    ]

    if any(keyword in message for keyword in purchase_keywords):
        return "PURCHASE"

    if any(keyword in message for keyword in investment_keywords):
        return "PURCHASE"

    # General gold questions
    if "gold" in message:
        return "GOLD"

    # SIP
    if "sip" in message:
        return "SIP"

    # Stocks
    if "stock" in message or "stocks" in message:
        return "STOCK"

    # Mutual funds
    if "mutual fund" in message or "mutual funds" in message:
        return "MUTUAL_FUND"

    return "GENERAL"
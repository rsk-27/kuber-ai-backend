import re


def extract_sip_action(message: str) -> tuple[str | None, int | None]:
    """
    Extract SIP action and SIP ID from a natural-language message.

    Examples:
        "Pause my SIP 2" -> ("PAUSE", 2)
        "Resume SIP 5" -> ("RESUME", 5)
        "Cancel my SIP 3" -> ("CANCEL", 3)
    """

    message = message.lower().strip()

    action = None

    if "pause" in message:
        action = "PAUSE"
    elif "resume" in message:
        action = "RESUME"
    elif "cancel" in message:
        action = "CANCEL"

    if action is None:
        return None, None

    match = re.search(
        r"\bsip\s*(?:id\s*)?(\d+)\b",
        message
    )

    if not match:
        return action, None

    sip_id = int(match.group(1))

    return action, sip_id


if __name__ == "__main__":
    test_messages = [
        "Pause my SIP 2",
        "Resume SIP 5",
        "Cancel my SIP 3",
        "Pause SIP ID 10",
        "Pause my SIP"
    ]

    for message in test_messages:
        action, sip_id = extract_sip_action(message)

        print(
            f"{message} -> "
            f"action={action}, sip_id={sip_id}"
        )
def route_task(user_input: str) -> str:
    """
    Decide which agent should handle the request.
    This file MUST stay dependency-free.
    """

    text = user_input.lower()

    # Policy number specific queries
    if "pol" in text:
        return "POLICY_DATA"

    # Quote related
    if any(k in text for k in ["quote", "price", "premium", "cost"]):
        return "QUOTE"

    # General policy questions
    if any(k in text for k in ["policy", "coverage", "benefit", "claim", "renew"]):
        return "POLICY"

    # Reminder
    if any(k in text for k in ["remind", "reminder"]):
        return "REMINDER"

    # CRM
    if any(k in text for k in ["crm", "customer"]):
        return "CRM"

    return "UNKNOWN"

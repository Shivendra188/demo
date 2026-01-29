from agents.policy_agent import handle_policy_query
from agents.quote_agent import generate_quote

def route_task(user_input: str):
    text = user_input.lower()

    policy_keywords = [
        "policy",
        "coverage",
        "benefits",
        "claim",
        "exclusion",
        "renewal",
        "insured"
    ]

    quote_keywords = [
        "quote",
        "price",
        "premium",
        "cost",
        "plan",
        "buy"
    ]

    # ---- POLICY AGENT ----
    if any(word in text for word in policy_keywords):
        return {
            "agent": "Policy Agent",
            "type": "POLICY",
            "response": handle_policy_query(user_input)
        }

    # ---- QUOTE AGENT ----
    if any(word in text for word in quote_keywords):
        # Example default values (can be improved later)
        payload = {
            "age": 30,
            "coverage_lakh": 5,
            "duration_years": 1
        }

        return {
            "agent": "Quote Agent",
            "type": "QUOTE",
            "response": generate_quote(payload)
        }

    # ---- FALLBACK ----
    return {
        "agent": "Supervisor",
        "type": "UNKNOWN",
        "response": "I can help with insurance quotes, policy details, renewals, and customer records."
    }

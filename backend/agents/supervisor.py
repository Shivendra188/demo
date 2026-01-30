

from agents.policy_agent import handle_policy_query
from agents.quote_agent import generate_quote

def route_task(user_input: str):
    text = user_input.lower()

    quote_keywords = [
        "quote", "price", "premium", "cost", "insurance plan"
    ]

    policy_keywords = [
        "policy", "coverage", "benefits", "claim",
        "exclusion", "renewal", "insured"
    ]

    if any(word in text for word in quote_keywords):
        return {
            "task": "QUOTE",
            "response": generate_quote(user_input)
        }

    if any(word in text for word in policy_keywords):
        return {
            "task": "POLICY",
            "response": handle_policy_query(user_input)
        }

    return {
        "task": "SUPERVISOR",
        "response": "I can help with policy details or insurance quotes."
    }

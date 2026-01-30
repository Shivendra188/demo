

from agents.policy_agent import run_policy_agent
from agents.quote_agent import run_quote

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
            "response": run_quote(user_input)
        }

    if any(word in text for word in policy_keywords):
        return {
            "task": "POLICY",
            "response": run_policy_agent(user_input)
        }

    return {
        "task": "SUPERVISOR",
        "response": "I can help with policy details or insurance quotes."
    }

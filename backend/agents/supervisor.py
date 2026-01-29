from agents.policy_agent import handle_policy_query

def route_task(user_input: str):
    policy_keywords = [
        "policy",
        "coverage",
        "benefits",
        "claim",
        "exclusion",
        "renewal",
        "insured",
        "premium"
    ]

    if any(word in user_input.lower() for word in policy_keywords):
        return {
            "agent": "Policy Agent",
            "response": handle_policy_query(user_input)
        }

    return {
        "agent": "Supervisor",
        "response": "This query is not policy-related."
    }

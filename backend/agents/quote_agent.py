


import json
import os

QUOTES_PATH = os.path.join(os.path.dirname(__file__), "..", "quotes.json")

def generate_quote(user_input: str):
    user_input = user_input.lower()

    if "health" in user_input:
        policy_type = "Health"
    elif "car" in user_input or "auto" in user_input:
        policy_type = "Car"
    elif "life" in user_input:
        policy_type = "Life"
    else:
        return {
            "agent": "Quote Agent",
            "response": "Please specify policy type: Health, Car, or Life."
        }

    with open(QUOTES_PATH, "r", encoding="utf-8") as f:
        quotes = json.load(f)

    filtered = [q for q in quotes if q["policy_type"] == policy_type]

    # sort by premium (₹xxxxx/year → extract number)
    filtered.sort(
        key=lambda x: int(
            x["premium"]
            .replace("₹", "")
            .replace("/year", "")
            .replace(",", "")
        )
    )

    top_quotes = filtered[:3]

    return {
        "agent": "Quote Agent",
        "policy_type": policy_type,
        "quotes": top_quotes
    }

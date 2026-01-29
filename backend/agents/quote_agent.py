def generate_quote(data: dict):
    policy_type = data.get("policy_type", "Health")

    return {
        "agent": "Quote Agent",
        "policy_type": policy_type,
        "coverage": "₹5,00,000",
        "premium": "₹12,000/year",
        "status": "Quote Generated"
    }

import langchain

# langchin / langGraph jo bhi use karke isko bhi banana hoga..  

# @tool
# def expiring_policies() -> str:
#     """List policies expiring in 30 days."""
#     res = supabase.table("policies").select("*, customers(name, phone)").eq("status", "Expiring").execute()
#     if not res.data:
#         return "No expiring policies"
#     return "\n".join([f"{p['policy_type']} {p['policy_id']} ({p['customers']['name']}) expires {p['policy_expiry']}" for p in res.data])

# @tool
# def expired_policies() -> str:
#     """List expired policies."""
#     res = supabase.table("policies").select("*, customers(name, phone)").eq("status", "Expired").execute()
#     return "\n".join([f"{p['policy_id']} ({p['customers']['name']}) expired {p['policy_expiry']}" for p in res.data]) if res.data else "No expired policies"

# @tool
# def reminder_campaign() -> str:
#     """Send reminders to ALL expiring policies."""
#     expiring = supabase.table("policies").select("*, customers(phone)").eq("status", "Expiring").execute()
#     sent = 0
#     for p in expiring.data:
#         # reminder_tool(p['customer_id'])  # Your Twilio
#         sent += 1
#     return f"Sent {sent} renewal reminders"

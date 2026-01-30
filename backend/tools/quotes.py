from langchain_core.tools import tool
from supabase import create_client
import os
from datetime import date, timedelta

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

@tool
def get_quote(customer_id: str, policy_type: str = None) -> str:
    """Generate renewal quote for customer."""
    
    # Fetch customer
    customer = supabase.table("customers").eq("customer_id", customer_id).execute().data
    if not customer:
        return f"❌ Customer {customer_id} not found"
    customer = customer[0]
    
    # Fetch current policy
    policy_query = supabase.table("policies").eq("customer_id", customer_id)
    if policy_type:
        policy_query = policy_query.eq("policy_type", policy_type)
    policy = policy_query.execute().data
    
    if not policy:
        return f"❌ No {policy_type or 'active'} policy for {customer_id}"
    policy = policy[0]
    
    # Calculate renewal quote (5% inflation + age factor)
    current_premium = float(policy["premium"])
    inflation_factor = 1.05
    age_factor = 1 + (int(customer.get("age", 30)) - 30) * 0.01
    
    new_premium = round(current_premium * inflation_factor * age_factor)
    hike_percent = round(((new_premium / current_premium) - 1) * 100)
    
    # Expiry + renewal dates
    expiry_date = date.fromisoformat(policy["expiry_date"].replace('/', '-'))
    renewal_start = expiry_date + timedelta(days=1)
    renewal_end = renewal_start + timedelta(days=365)
    
    quote = {
        "quote_id": f"Q{date.today().strftime('%y%m%d')}{customer_id[-3:]}",
        "customer_name": customer["name"],
        "customer_phone": customer["phone"],
        "policy_type": policy["policy_type"],
        "current_insurer": policy["insurer"],
        "current_premium": f"₹{current_premium:,}",
        "new_premium": f"₹{new_premium:,}/year",
        "hike_percent": f"{hike_percent}% ↑",
        "coverage_amount": "₹10 Lakhs",  # From your sample
        "tenure": "1 Year",
        "validity_days": 15,
        "renewal_start": renewal_start.strftime("%d/%m/%Y"),
        "expiry_date": expiry_date.strftime("%d/%m/%Y")
    }
    
    return quote

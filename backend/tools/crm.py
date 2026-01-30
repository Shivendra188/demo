from langchain_core.tools import tool
from pydantic import BaseModel, Field, validator
from typing import Optional
from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

class UpdateCustomer(BaseModel):
    """Update customer details."""
    customer_id: str = Field(..., description="Customer ID like CUST0001")
    phone: Optional[str] = Field(None, description="New phone number")
    name: Optional[str] = Field(None, description="New name")
    email: Optional[str] = Field(None, description="New email")

    @validator("customer_id")
    def validate_id(cls, v):
        if not v.startswith("CUST"):
            raise ValueError("Must be CUSTXXXX format")
        return v

@tool
def crm_update(input: UpdateCustomer) -> str:
    """Update customer details in Supabase (phone/name/email).
    
    Example: customer_id='CUST0001', phone='9876543210'
    """
    # Fetch current customer
    existing = supabase.table("customers").select("*").eq("customer_id", input.customer_id).execute().data
    
    if not existing:
        return f"❌ Customer {input.customer_id} not found"
    
    current = existing[0]
    
    # Prepare updates
    updates = {}
    if input.phone:
        updates["phone"] = input.phone
    if input.name:
        updates["name"] = input.name
    if input.email:
        updates["email"] = input.email
    
    if not updates:
        return f"ℹ️ No changes specified for {input.customer_id}"
    
    # Update Supabase
    result = supabase.table("customers").update(updates).eq("customer_id", input.customer_id).execute()
    
    if result.data:
        return f"""
CRM Update Complete!
{input.customer_id}
- Name: {result.data[0]["name"]}
- Phone: {result.data[0]["phone"]}
- Email: {result.data[0]["email"]}
Updated: {len(updates)} fields
        """
    else:
        return f"Update failed for {input.customer_id}"

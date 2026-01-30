from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from datetime import date
import os
from dotenv import load_dotenv


# Load environment variables
load_dotenv()

# ===== Agents =====
from agents.supervisor import route_task
from agents.quote_agent import run_quote  # ✅ New import
from agents.policy_agent import handle_policy_query
from agents.reminder_agent import run_reminder_agent
from agents.crm_agent import run_crm_agent

# ===== Services =====
from services.whatsapp import send_whatsapp_message
from supabase import create_client

app = FastAPI()

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== Models =====
class ChatRequest(BaseModel):
    message: str
    policy_number: str | None = None

class WhatsAppMessage(BaseModel):
    phone: str
    message: str

# ===== Root =====
@app.get("/")
def root():
    return {"status": "Insurance AI Copilot Backend Running"}

# ===== Chat =====
@app.post("/chat")
def chat(request: ChatRequest):
    task = route_task(request.message)

    if task == "QUOTE":
        return run_quote(request.dict())

    if task == "POLICY":
        answer = handle_policy_query(request.message)
        return {
            "response": answer,
            "task_type": "POLICY"
        }

    if task == "REMINDER":
        result = run_reminder_agent(request.message)
        return {
            "response": result,
            "task_type": "REMINDER"
        }

    if task == "CRM":
        result = run_crm_agent(request.message)
        return {
            "response": result,
            "task_type": "CRM"
        }

    return {"error": "Could not understand request"}

# ===== Supabase (SECURE) =====
 

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


# ===== CRM Dashboard =====
@app.get("/crm-dashboard")
def crm_dashboard():
    try:
        # 1. Fetch data
        response = (
            supabase.table("policies")
            .select("*, customers(*)")
            .limit(50)
            .execute()
        )
        
        # Check if response has data attribute
        data = response.data if hasattr(response, 'data') else response
        
        print(f"DEBUG: Raw data count: {len(data) if data else 0}")

        today = date.today()
        table_data = []

        if not data:
            return {"data": [], "total": 0}

        for row in data:
            # Match CSV column names exactly
            # Your CSV shows 'expiry_date', not 'policy_expiry'
            expiry = row.get("expiry_date")
            status = row.get("status", "Active")

            if expiry:
                try:
                    # Handle different date formats (YYYY-MM-DD vs D/M/YYYY)
                    # If date is '4/3/2026', string comparison might fail. 
                    # For now, we'll keep it simple:
                    if str(expiry) < str(today):
                        status = "Expired"
                except:
                    pass

            # Safe navigation for the joined customer table
            customer_info = row.get("customers")
            
            # This handles cases where customer_id in policies doesn't match 
            # any record in the customers table
            if isinstance(customer_info, dict):
                customer_name = customer_info.get("name", "Unknown")
                customer_phone = customer_info.get("phone", "N/A")
            else:
                customer_name = "Unknown (Missing Link)"
                customer_phone = "N/A"

            table_data.append({
                "name": customer_name,
                "phone": customer_phone,
                "policy_type": row.get("policy_type", "N/A"),
                "policy_id": row.get("policy_id", "N/A"),
                "status": status,
            })

        return {
            "data": table_data,
            "total": len(table_data),
            "updated": str(today)
        }

    except Exception as e:
        # This will print the EXACT error in your terminal
        print(f"CRITICAL ERROR: {str(e)}")
        return {"error": str(e), "data": []}

# ===== Customers =====
@app.get("/customers")
def get_customers(limit: int = 10):
    return supabase.table("customers").select("*").limit(limit).execute().data

# ===== Policies =====
@app.get("/policies")
def get_policies(limit: int = 10):
    return supabase.table("policies").select("*").limit(limit).execute().data

# ===== Expiring =====
@app.get("/expiring")
def expiring():
    return (
        supabase.table("policies")
        .select("*, customers(name)")
        .lte("policy_expiry", "2026-02-28")
        .execute()
        .data
    )

# ===== WhatsApp =====
@app.post("/send-reminder")
def send_reminder(msg: WhatsAppMessage):
    send_whatsapp_message(msg)
    return {"status": "sent"}

# ===== Batch =====
@app.post("/batch-reminders")
def batch_reminders():
    expiring = (
        supabase.table("policies")
        .select("*, customers(phone, name)")
        .eq("status", "Expiring")
        .execute()
    )

    results = []
    for p in expiring.data:
        msg = (
            f"Hello {p['customers']['name']}, "
            f"your {p['policy_type']} policy {p['policy_id']} "
            f"expires {p['policy_expiry']}."
        )

        send_whatsapp_message(
            WhatsAppMessage(
                phone=p["customers"]["phone"],
                message=msg
            )
        )
        results.append(p["policy_id"])

    return {"sent_to": len(results), "policies": results}

# ===== CRM (chat-based) =====
@app.post("/crm")
def crm_endpoint(request: dict):
    user_input = request["message"]
    result = run_crm_agent(user_input)
    return {"response": result, "task_type": "CRM"}
  

class QuoteRequest(BaseModel):
    message: str
    customer_id: str = None

@app.post("/crm")
async def crm_endpoint(request: QuoteRequest):
    result = run_crm_agent(request.message)
    return {"response": result, "task_type": "CRM"}
 

@app.post("/quote-agent")
async def quote_agent_endpoint(request: dict):
    """Quote Agent API."""
    message = request.get("message", "")
    result = run_quote(message)
    return {"response": result, "input": message}

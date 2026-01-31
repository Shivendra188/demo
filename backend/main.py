from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
from datetime import date
import os
from dotenv import load_dotenv

# =========================
# LOAD ENV
# =========================
load_dotenv()

# =========================
# AGENTS
# =========================
from agents.supervisor import route_task
from agents.policy_agent import handle_policy_query
from agents.policy_data_agent import handle_policy_data_query
from agents.quote_agent import generate_quote
from agents.reminder_agent import run_reminder_agent
from agents.crm_agent import run_crm_agent

# =========================
# SERVICES
# =========================
from services.whatsapp import send_whatsapp_message
from supabase import create_client

# =========================
# APP
# =========================
app = FastAPI()

# =========================
# CORS
# =========================
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# =========================
# MODELS
# =========================
class ChatRequest(BaseModel):
    message: str
    policy_number: Optional[str] = None

class WhatsAppMessage(BaseModel):
    phone: str
    message: str

# =========================
# ROOT
# =========================
@app.get("/")
def root():
    return {"status": "Insurance AI Copilot Backend Running"}

# =========================
# CHAT (MAIN ENTRY)
# =========================
@app.post("/chat")
def chat(request: ChatRequest):
    task = route_task(request.message)
    message = request.message

    if task == "POLICY_DATA":
        return {
            "task_type": "POLICY_DATA",
            "response": handle_policy_data_query(message),
        }

    if task == "POLICY":
        return {
            "task_type": "POLICY",
            "response": handle_policy_query(message),
        }

    if task == "QUOTE":
        return {
            "task_type": "QUOTE",
            "response": generate_quote(request.model_dump()),
        }

    if task == "REMINDER":
        return {
            "task_type": "REMINDER",
            "response": run_reminder_agent(message),
        }

    if task == "CRM":
        return {
            "task_type": "CRM",
            "response": run_crm_agent(message),
        }

    return {
        "task_type": "UNKNOWN",
        "response": "I can help with policy details, policy numbers, or insurance quotes.",
    }

# =========================
# SUPABASE
# =========================
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# =========================
# CRM DASHBOARD
# =========================
@app.get("/crm-dashboard")
def crm_dashboard():
    try:
        response = (
            supabase.table("policies")
            .select("*, customers(*)")
            .limit(50)
            .execute()
        )

        data = response.data or []
        today = date.today()
        table_data = []

        for row in data:
            expiry = row.get("expiry_date")
            status = row.get("status", "Active")

            if expiry and str(expiry) < str(today):
                status = "Expired"

            customer = row.get("customers") or {}
            table_data.append({
                "name": customer.get("name", "Unknown"),
                "phone": customer.get("phone", "N/A"),
                "policy_type": row.get("policy_type", "N/A"),
                "policy_id": row.get("policy_id", "N/A"),
                "status": status,
            })

        return {
            "data": table_data,
            "total": len(table_data),
            "updated": str(today),
        }

    except Exception as e:
        return {"error": str(e), "data": []}

# =========================
# CUSTOMERS
# =========================
@app.get("/customers")
def get_customers(limit: int = 10):
    return supabase.table("customers").select("*").limit(limit).execute().data

# =========================
# POLICIES
# =========================
@app.get("/policies")
def get_policies(limit: int = 10):
    return supabase.table("policies").select("*").limit(limit).execute().data

# =========================
# WHATSAPP
# =========================
@app.post("/send-reminder")
def send_reminder(msg: WhatsAppMessage):
    send_whatsapp_message(msg)
    return {"status": "sent"}
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
# =========================
# CRM (CHAT-BASED)
# =========================
@app.post("/crm")
def crm_endpoint(request: dict):
    message = request.get("message", "")
    return {
        "task_type": "CRM",
        "response": run_crm_agent(message),
    }

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
from agents.quote_agent import generate_quote
from agents.policy_agent import handle_policy_query
from agents.reminder_agent import send_renewal_reminder, run_reminder_agent
from agents.crm_agent import update_crm, run_crm_agent

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
        return generate_quote(request.dict())

    if task == "POLICY":
        return handle_policy_query(request.message)

    if task == "REMINDER":
        result = run_reminder_agent(request.message)
        return {"response": result, "task_type": "REMINDER"}

    if task == "CRM":
        return {"response": result, "task_type": "CRM"}

    return {"error": "Could not understand request"}

# ===== Supabase (SECURE) =====
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# ===== CRM Dashboard =====
@app.get("/crm-dashboard")
def crm_dashboard() -> Dict:
    data = (
        supabase.table("policies")
        .select("*, customers(name, phone)")
        .limit(50)
        .execute()
        .data
    )

    today = date.today()
    table_data = []

    for row in data:
        expiry = row["policy_expiry"]
        status = row.get("status", "Active")

        if expiry < str(today):
            status = "Expired"

        table_data.append({
            "name": row["customers"]["name"],
            "policy": f"{row['policy_type']} ({row['policy_id']})",
            "expiry": expiry,
            "premium": f"₹{int(row.get('premium', 0)):,}",
            "status": status
        })

    return {
        "data": table_data,
        "total": len(table_data),
        "updated": str(today)
    }

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
        msg = f"Hello {p['customers']['name']}, your {p['policy_type']} policy {p['policy_id']} expires {p['policy_expiry']}."
        send_whatsapp_message(
            WhatsAppMessage(
                phone=p["customers"]["phone"],
                message=msg
            )
        )
        results.append(p["policy_id"])

    return {"sent_to": len(results), "policies": results}


#crm

@app.post("/crm")
def crm_endpoint(request: dict):
    user_input = request["message"]
    result = run_crm_agent(user_input)
    return {"response": result, "task_type": "CRM"}
 
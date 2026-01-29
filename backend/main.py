from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict
from datetime import date
import os

# ===== Agents =====
from agents.supervisor import route_task
from agents.quote_agent import generate_quote
from agents.policy_agent import handle_policy_query
from agents.reminder_agent import send_renewal_reminder
from agents.crm_agent import update_crm

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
        return send_renewal_reminder()

    if task == "CRM":
        return update_crm(request.dict())

    return {"error": "Could not understand request"}

<<<<<<< HEAD
supabase = create_client("https://ljepgqjlwtvxotzgdikp.supabase.co", "sb_publishable_FJWN3AMGacjf45jCfhVyAA_ZrAUmQGg")
  
@app.get("/crm-dashboard")
def crm_dashboard() -> Dict:
    """CRM data: JOIN policies + customers."""
    data = supabase.table("policies").select("""
        *,
        customers(name, phone)
    """).limit(50).execute().data

    today = date.today()
=======
# ===== Supabase =====
supabase = create_client(
    os.getenv("https://ljepgqjlwtvxotzgdikp.supabase.com"),
    os.getenv("sb_publishable_FJWN3AMGacjf45jCfhVyAA_ZrAUmQGg")
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
>>>>>>> fd79aeb (policy)

    table_data = []
    for row in data:
        # Simple status logic (you can adjust)
        expiry_str = row["policy_expiry"]
        status = row.get("status")
        if not status:
            status = "Active"
            if expiry_str < str(today):
                status = "Expired"

        table_data.append({
            "name": row["customers"]["name"],
<<<<<<< HEAD
            "phone": row["customers"]["phone"],
            "policy_type": row["policy_type"],
            "policy_id": row["policy_id"],
            "expiry": row["policy_expiry"],
            "premium": row.get("premium"),
            "status": status,
=======
            "policy": f"{row['policy_type']} ({row['policy_id']})",
            "expiry": row["policy_expiry"],
            "premium": f"₹{int(row.get('premium', 0)):,}",
            "status": row.get("status", "Active")
>>>>>>> fd79aeb (policy)
        })

    return {
        "data": table_data,
        "total": len(table_data),
        "updated": str(today),
    }

<<<<<<< HEAD

=======
# ===== Customers =====
>>>>>>> fd79aeb (policy)
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

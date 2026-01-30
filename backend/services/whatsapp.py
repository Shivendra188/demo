from pydantic import BaseModel
from twilio.rest import Client
import os

from typing import Optional, Dict
from datetime import date, timedelta
from supabase import create_client

# --- Configuration (Pulled from Environment) ---
ACC_SID = os.getenv('ACC_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')


client = Client(ACC_SID, AUTH_TOKEN)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
class Message(BaseModel):
    phone: str 
    message: str

 
def send_whatsapp_message(msg: Message):
    from_num = 'whatsapp:+14155238886'  # YOUR sandbox number
    to_num = f'whatsapp:+{msg.phone}'
    
    body_text = f"Insurance Copilot\n{msg.message}"
    
    try:
        message = client.messages.create(
            body=body_text,
            from_=from_num,
            to=to_num
        )
        print(f"✅ SUCCESS SID: {message.sid}")
        return {"status": "sent", "sid": message.sid}
    except Exception as e:
        print(f"❌ FULL ERROR: {e}")
        return {"error": str(e)}

def send_renewal_reminder(customer_id: Optional[str] = None) -> Dict:
    """Send reminders to expiring policies (batch or single)."""
    today = date.today()
    expiry_threshold = today + timedelta(days=30)  # 30 days
    
    # Get expiring policies
    query = supabase.table("policies").select("""
        *,
        customers(name, phone)
    """).lte("policy_expiry", str(expiry_threshold))
    
    if customer_id:
        query = query.eq("customer_id", customer_id)
    
    data = query.execute().data
    
    if not data:
        return {"status": "no_targets", "message": "No expiring policies found"}
    
    results = []
    for row in data:
        phone = row["customers"]["phone"]
        name = row["customers"]["name"]
        policy_id = row["policy_id"]
        expiry = row["policy_expiry"]
        
        msg_body = f"""
Hi {name}! 

Your policy {policy_id} expires on {expiry}.
Renew now to avoid lapse → bit.ly/renewal-link

Insurance Copilot
Sent: {today.strftime('%d %b %Y')}
        """
        
        msg = Message(phone=phone, message=msg_body.strip())
        result = send_whatsapp_message(msg)
        results.append(result)
    
    success = len([r for r in results if r["status"] == "sent"])
    return {
        "status": "completed",
        "sent": success,
        "total": len(results),
        "targets": len(data),
        "results": results[-5:]  # Last 5 for demo
    }

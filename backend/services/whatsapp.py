from pydantic import BaseModel
from twilio.rest import Client
import os


# --- Configuration (Pulled from Environment) ---
ACC_SID = os.getenv('ACC_SID')
AUTH_TOKEN = os.getenv('AUTH_TOKEN')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER')

  
client = Client(ACC_SID, AUTH_TOKEN)
class Message(BaseModel):
    phone: str 
    message: str

 
def send_whatsapp_message(msg: Message):
    from_num = 'whatsapp:+14155238886'  # YOUR sandbox number
    to_num = f'whatsapp:{msg.phone}'
    
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

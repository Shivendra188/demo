from langchain_core.tools import tool
from services.whatsapp import send_renewal_reminder
from datetime import date, timedelta

@tool
def reminder_tool(customer_id: str = None) -> str:
    """Send WhatsApp renewal reminders to expiring policies (batch/single).
    
    Args:
        customer_id: Specific customer ID (optional). None = ALL expiring.
    
    Returns batch results.
    """
    result = send_renewal_reminder(customer_id)
    
    if result["status"] == "no_targets":
        return "ℹ️ No expiring policies found (within 30 days)."
    
    return f"""
Reminder Agent Complete!
Sent: {result['sent']}/{result['total']}
Targets: {result['targets']}
Threshold: 30 days from today

Last 3 results:
{chr(10).join([f"• {r['phone'][:8]}...: {r['status']}" for r in result.get('results', [])[-3:]])}
"""

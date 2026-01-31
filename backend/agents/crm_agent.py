import os
from typing import List, Dict, Optional
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode

# =========================
# LOAD GROQ API KEY
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================
# SAFE LLM INIT
# =========================
llm: Optional[ChatGroq] = None

if GROQ_API_KEY:
    try:
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0.1,
            max_tokens=300,
        )
    except Exception:
        llm = None


# =========================
# TOOL FUNCTIONS (MUST HAVE DOCSTRINGS)
# =========================
def lookup_customer(name: str, crm_data: List[Dict]) -> str:
    """
    Look up a customer by name from CRM records.
    Returns customer details if found.
    """
    for c in crm_data:
        if c.get("name", "").lower() == name.lower():
            return str(c)
    return "Customer not found in records."


def list_active_customers(crm_data: List[Dict]) -> str:
    """
    List all active customers from CRM records.
    """
    active = [c for c in crm_data if c.get("status") == "Active"]
    return str(active) if active else "No active customers found."


# =========================
# TOOLS LIST (IMPORTANT)
# =========================
tools = [lookup_customer, list_active_customers]


# =========================
# AGENT STATE
# =========================
def crm_agent(state: Dict) -> Dict:
    """
    CRM agent logic that decides how to answer the user query.
    """
    user_input = state.get("input", "")
    crm_data = state.get("crm_data", [])

    if not user_input:
        return {"output": "Please ask a valid CRM question."}

    if not crm_data:
        return {"output": "No CRM data available."}

    if llm is None:
        return {"output": "CRM service temporarily unavailable."}

    response = llm.invoke(
        f"""
You are a CRM assistant.

User question:
{user_input}

Available CRM data:
{crm_data}

Respond briefly.
"""
    )

    return {"output": response.content}


# =========================
# LANGGRAPH WORKFLOW
# =========================
workflow = StateGraph(dict)

workflow.add_node("crm_agent", crm_agent)
workflow.add_node("tools", ToolNode(tools))

workflow.set_entry_point("crm_agent")
workflow.add_edge("crm_agent", END)

graph = workflow.compile()


# =========================
# PUBLIC ENTRY POINT
# (USED BY main.py)
# =========================
def run_crm_agent(user_input: str, crm_data: List[Dict]) -> str:
    """
    Entry point to run the CRM agent workflow.
    """
    result = graph.invoke(
        {
            "input": user_input,
            "crm_data": crm_data,
        }
    )
    return result.get("output", "No response generated.")

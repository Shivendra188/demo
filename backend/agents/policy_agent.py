# backend/agents/policy_agent.py
from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
import operator
import re
import json
from datetime import date, timedelta
from supabase import create_client
import os

supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))
llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant")

class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

def policy_search_node(state: State):
    """Search policies (expiring, by type/customer)."""
    msg = state["messages"][-1].content.lower()
    # Parse: "expiring", "car CUST0001", "POL123"
    pol_match = re.search(r'(POL\d+)', msg)
    cust_match = re.search(r'(CUST\d+)', msg)
    
    try:
        if 'expiring' in msg:
            # Expiring in <30 days
            policies = supabase.table("policies").select("policy_id, policy_type, customer_id, customers(name), expiry_date").lte("expiry_date", (date.today() + timedelta(days=30)).isoformat()).execute()
        elif pol_match:
            pol_id = pol_match.group()
            policies = supabase.table("policies").select("*").eq("policy_id", pol_id).execute()
        elif cust_match:
            cust_id = cust_match.group()
            policies = supabase.table("policies").select("*").eq("customer_id", cust_id).execute()
        else:
            policies = supabase.table("policies").select("policy_id, policy_type, customer_id").limit(5).execute()
        
        content = json.dumps({"policies": policies.data}) if policies.data else "No policies found"
    except Exception as e:
        content = json.dumps({"error": str(e)})
    
    return {"messages": [ToolMessage(content=content, tool_call_id="policy_search")]}

def policy_update_node(state: State):
    """Update: lapse/renew status + expiry."""
    msg = state["messages"][-1].content.lower()
    pol_match = re.search(r'(POL\d+)', msg)
    
    if not pol_match:
        content = "❌ Specify policy_id (POL123)"
        return {"messages": [ToolMessage(content=content, tool_call_id="policy_update")]}
    
    pol_id = pol_match.group()
    if 'renew' in msg:
        updates = {
            "status": "Active",
            "expiry_date": (date.today() + timedelta(days=365)).isoformat()
        }
    elif 'lapse' in msg:
        updates = {"status": "Lapsed"}
    else:
        content = "❌ Use 'renew' or 'lapse'"
        return {"messages": [ToolMessage(content=content, tool_call_id="policy_update")]}
    
    try:
        result = supabase.table("policies").update(updates).eq("policy_id", pol_id).execute()
        content = f"✅ {pol_id} {updates['status']}" if result.data else "❌ Update failed"
    except Exception as e:
        content = f"❌ Error: {str(e)}"
    
    return {"messages": [ToolMessage(content=content, tool_call_id="policy_update")]}

def router_node(state: State) -> dict:
    msg = state["messages"][-1].content.lower()
    if any(word in msg for word in ['search', 'find', 'expiring']):
        return {"next": "policy_search"}
    elif any(word in msg for word in ['update', 'renew', 'lapse']):
        return {"next": "policy_update"}
    return {"next": "agent"}

def agent_llm(state: State):
    messages = state["messages"][-1:]
    return {"messages": [llm.invoke(messages)]}

# Graph
workflow = StateGraph(State)
workflow.add_node("router", router_node)
workflow.add_node("policy_search", policy_search_node)
workflow.add_node("policy_update", policy_update_node)
workflow.add_node("agent", agent_llm)

workflow.add_edge(START, "router")
workflow.add_conditional_edges(
    "router",
    lambda s: router_node(s)["next"],
    {"policy_search": "policy_search", "policy_update": "policy_update", "agent": "agent"}
)
workflow.add_edge("policy_search", END)
workflow.add_edge("policy_update", END)
workflow.add_edge("agent", END)

policy_agent = workflow.compile()

def run_policy_agent(user_input: str):
    result = policy_agent.invoke({"messages": [HumanMessage(content=user_input)]})
    return result["messages"][-1].content

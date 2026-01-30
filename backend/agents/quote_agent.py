from typing import TypedDict, Annotated, Sequence, Literal
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
from langgraph.prebuilt import ToolNode  # Not used here but kept for ref
import operator
import re
import os
import json
from datetime import date
from supabase import create_client

# Supabase (global)
supabase = create_client(os.getenv("SUPABASE_URL"), os.getenv("SUPABASE_KEY"))

llm = ChatGroq(groq_api_key=os.getenv("GROQ_API_KEY"), model_name="llama-3.1-8b-instant")

# State
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# 🔥 DIRECT FUNCTIONS (unchanged - your Supabase fixes are correct)
def calculate_premium(state: State):
    """Premium calculation node."""
    last_msg = state["messages"][-1]
    
    # Parse args from previous tool call
    if hasattr(last_msg, 'tool_calls') and last_msg.tool_calls:
        args = last_msg.tool_calls[0]['args']
        customer_id = args.get('customer_id', 'CUST0001')
        policy_type = args.get('policy_type', 'Health')
    else:
        # Fallback parse
        content = last_msg.content.lower()
        customer_match = re.search(r'(CUST\\d+)', content)
        policy_match = re.search(r'(health|life|car)', content)
        customer_id = customer_match.group() if customer_match else 'CUST0001'
        policy_type = policy_match.group().title() if policy_match else 'Health'
    
    try:
        # Fetch data - FIXED: select() before eq()
        customers = (
            supabase.table("customers")
            .select("*")
            .eq("customer_id", customer_id)
            .execute()
        )
        customer = customers.data[0] if customers.data else None
        
        policies = (
            supabase.table("policies")
            .select("*")
            .eq("customer_id", customer_id)
            .eq("policy_type", policy_type)
            .execute()
        )
        policy = policies.data[0] if policies.data else None
        
        if not customer or not policy:
            content = json.dumps({"error": f"No data for {customer_id}/{policy_type}"})
        else:
            # REAL CALC
            base = {"Health": 15000, "Life": 10000, "Car": 8000}.get(policy_type, 12000)
            age_f = 1 + max(0, (customer.get("age", 30) - 25) * 0.015)
            city_f = {"Delhi": 1.10, "Mumbai": 1.15, "Bangalore": 1.05}.get(customer.get("city"), 1.0)
            claims_f = 1 + customer.get("claims_history", 0) * 0.20
            inflation = 1.06
            
            new_premium = round(base * age_f * city_f * claims_f * inflation)
            hike = round((new_premium / float(policy["premium"]) - 1) * 100)
            
            content = json.dumps({
                "quote_id": f"Q{customer_id[-3:]}-{date.today().strftime('%y%m')}",
                "customer": customer["name"],
                "risk": {
                    "age": f"{customer.get('age', '?')} → {age_f:.2f}x",
                    "city": f"{customer.get('city', '?')} → {city_f:.2f}x",
                    "claims": f"{customer.get('claims_history', 0)} → {claims_f:.2f}x"
                },
                "current": f"₹{float(policy['premium']):,.0f}",
                "new": f"₹{new_premium:,.0f}/yr",
                "hike": f"{hike}% ↑"
            })
    
    except Exception as e:
        content = json.dumps({"error": str(e)})
    
    return {
        "messages": [ToolMessage(
            content=content,
            tool_call_id="premium_calc",
            name="calculate_premium"
        )]
    }

def crm_update_node(state: State):
    """CRM update node."""
    last_msg = state["messages"][-1]
    args = last_msg.tool_calls[0]['args'] if last_msg.tool_calls else {}
    
    customer_id = args.get('customer_id')
    updates = {k: args[k] for k in ['phone', 'name', 'email'] if k in args}
    
    if updates:
        result = (
            supabase.table("customers")
            .update(updates)
            .eq("customer_id", customer_id)
            .execute()
        )
        content = "✅ Updated!" if result.data else "❌ Update failed"
    else:
        content = "No updates specified"
    
    return {"messages": [ToolMessage(content=content, tool_call_id="crm_update")]}

# FIXED ROUTER: Now a proper node
# FIXED ROUTER: Returns dict with "next" key
def router_node(state: State) -> dict:
    """Router node - returns {"next": "target_node"}."""
    msg = state["messages"][-1].content.lower()
    if any(word in msg for word in ['quote', 'renew', 'premium']):
        return {"next": "premium_calc"}  # 🔑 Dict format
    elif any(word in msg for word in ['update', 'change']):
        return {"next": "crm_update"}
    return {"next": "agent"}

# In graph build: Use simple lambda for conditional


# Agent LLM
def agent_llm(state: State):
    messages = state["messages"][-1:]
    return {"messages": [llm.invoke(messages)]}

# Build Graph - FIXED
workflow = StateGraph(State)

# Add ALL nodes FIRST (including router)
workflow.add_node("router", router_node)  # 🔑 MISSING: Add router as node
workflow.add_node("premium_calc", calculate_premium)
workflow.add_node("crm_update", crm_update_node)
workflow.add_node("agent", agent_llm)

# Entry from START → router
workflow.add_edge(START, "router")

# Conditional from router
workflow.add_conditional_edges(
    "router",
    lambda state: router_node(state)["next"],  # Extract "next" string
    {
        "premium_calc": "premium_calc",
        "crm_update": "crm_update", 
        "agent": "agent"
    }
)

# Tool ends
workflow.add_edge("premium_calc", END)
workflow.add_edge("crm_update", END)
workflow.add_edge("agent", END)

agent = workflow.compile()

def run_quote(user_input: str):
    """Run agent."""
    result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
    return result["messages"][-1].content

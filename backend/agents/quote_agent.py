from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END, START
import operator
import re
import os
import json
from datetime import date
from supabase import create_client

# =========================
# SUPABASE
# =========================
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

# =========================
# LLM
# =========================
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

# =========================
# STATE
# =========================
class State(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# =========================
# PREMIUM CALCULATION NODE
# =========================
def calculate_premium(state: State):
    last_msg = state["messages"][-1]
    content = last_msg.content.lower()

    customer_id = (
        re.search(r"(cust\d+)", content).group().upper()
        if re.search(r"(cust\d+)", content)
        else "CUST0001"
    )

    policy_type = (
        re.search(r"(health|life|car)", content).group().title()
        if re.search(r"(health|life|car)", content)
        else "Health"
    )

    try:
        customers = (
            supabase.table("customers")
            .select("*")
            .eq("customer_id", customer_id)
            .execute()
        )
        customer = customers.data[0] if customers.data else None

        if not customer:
            return {
                "messages": [
                    ToolMessage(
                        content=json.dumps({"error": "Customer not found"}),
                        tool_call_id="premium_calc",
                    )
                ]
            }

        policies = (
            supabase.table("policies")
            .select("*")
            .eq("customer_id", customer_id)
            .eq("policy_type", policy_type)
            .execute()
        )
        existing_policy = policies.data[0] if policies.data else None

        base = {"Health": 15000, "Life": 10000, "Car": 8000}.get(policy_type, 12000)
        age_f = 1 + max(0, (customer.get("age", 30) - 25) * 0.015)
        city_f = {"Delhi": 1.10, "Mumbai": 1.15, "Bangalore": 1.05}.get(
            customer.get("city"), 1.0
        )
        claims_f = 1 + customer.get("claims_history", 0) * 0.20
        inflation = 1.06

        new_premium = round(base * age_f * city_f * claims_f * inflation)

        response = {
            "quote_id": f"Q{customer_id[-3:]}-{date.today().strftime('%y%m')}",
            "customer": customer["name"],
            "policy_type": policy_type,
            "calculated_premium": f"₹{new_premium:,.0f}/yr",
        }

        if existing_policy:
            old = float(existing_policy["premium"])
            hike = round((new_premium / old - 1) * 100)
            response.update(
                {
                    "type": "RENEWAL",
                    "current_premium": f"₹{old:,.0f}",
                    "hike": f"{hike}% ↑",
                }
            )
        else:
            response.update(
                {
                    "type": "NEW_POLICY_QUOTE",
                    "note": "No existing policy found. Fresh quote generated.",
                }
            )

        return {
            "messages": [
                ToolMessage(
                    content=json.dumps(response),
                    tool_call_id="premium_calc",
                )
            ]
        }

    except Exception as e:
        return {
            "messages": [
                ToolMessage(
                    content=json.dumps({"error": str(e)}),
                    tool_call_id="premium_calc",
                )
            ]
        }

# =========================
# ROUTER NODE
# =========================
def router_node(state: State) -> dict:
    msg = state["messages"][-1].content.lower()

    if any(k in msg for k in ["quote", "renew", "premium"]):
        return {"next": "premium_calc"}

    return {"next": "agent"}

# =========================
# FALLBACK AGENT
# =========================
def agent_llm(state: State):
    messages = state["messages"][-1:]
    return {"messages": [llm.invoke(messages)]}

# =========================
# BUILD GRAPH
# =========================
workflow = StateGraph(State)

workflow.add_node("router", router_node)
workflow.add_node("premium_calc", calculate_premium)
workflow.add_node("agent", agent_llm)

workflow.add_edge(START, "router")

workflow.add_conditional_edges(
    "router",
    lambda s: router_node(s)["next"],
    {
        "premium_calc": "premium_calc",
        "agent": "agent",
    },
)

workflow.add_edge("premium_calc", END)
workflow.add_edge("agent", END)

quote_agent = workflow.compile()

# =========================
# INTERNAL RUNNER
# =========================
def run_quote(user_input: str) -> str:
    result = quote_agent.invoke(
        {"messages": [HumanMessage(content=user_input)]}
    )
    return result["messages"][-1].content

# =========================
# 🔑 PUBLIC API (USED BY main.py)
# =========================
def generate_quote(data: dict) -> str:
    """
    This function is REQUIRED by main.py
    Input: { "message": "string" }
    """
    message = data.get("message", "")
    return run_quote(message)

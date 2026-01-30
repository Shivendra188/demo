from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
import operator
import re
import os

# Import TOOLS
from tools.crm import crm_update
from  .quote_agent import calculate_premium  # ✅ New tool

tools = [crm_update, calculate_premium]  # ✅ Real tool

# State
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# LLM + TOOLS
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

llm_with_tools = llm.bind_tools(tools)

# 🔥 FIXED PARSER - Handles QUOTE + UPDATE
def crm_parser(state: AgentState):
    user_input = state["messages"][-1].content.lower()
    
    # ✅ FIXED: Quote pattern - CUST optional now
    quote_match = re.search(r"(?:renew|quote|get)\s*(health|life|car)?(?:\s+(CUST\d+))?", user_input)
    if quote_match:
        policy_type = quote_match.group(1)
        customer_id = quote_match.group(2) or "CUST0001"  # Default
        
        tool_input = {"customer_id": customer_id}
        if policy_type: 
            tool_input["policy_type"] = policy_type.title()
        
        return {
            "messages": [AIMessage(
                content=f"🔄 Quote for {customer_id} ({tool_input.get('policy_type', 'any')})",
                tool_calls=[{
                    "name": "generate_quote",
                    "args": tool_input,
                    "id": f"quote_{customer_id}"
                }]
            )]
        }
    
    # Rest of update logic...

    
    # 2. UPDATE commands
    update_patterns = [
        r"(?:update|change|set)\s+(CUST\d+)\s+(phone|name|email)\s+(.+?)(?:\s|$)",
        r"(?:update|change|set)\s+(CUST\d+)\s+(.+?)\s+to\s+(.+?)(?:\s|$)"
    ]
    
    for pattern in update_patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            customer_id, field_type, field_value = match.groups()
            tool_input = {"customer_id": customer_id}
            tool_input[field_type] = field_value.strip()
            
            return {
                "messages": [AIMessage(
                    content=f"✅ Updating {customer_id} {field_type} → {field_value}",
                    tool_calls=[{
                        "name": "crm_update",
                        "args": tool_input,
                        "id": f"update_{customer_id}"
                    }]
                )]
            }
    
    # ❌ Invalid command
    return {
        "messages": [AIMessage(content="""❌ Commands:
• `quote health CUST0001` - Get renewal quote
• `update CUST0001 phone 9876543210` - Update details""")]
    }

# Agent handles tool responses
def agent_node(state: AgentState):
    """Process tool results."""
    messages = state["messages"]
    last_message = messages[-1]
    
    if isinstance(last_message, ToolMessage):
        # Quote result → Offer WhatsApp/send
        if "quote_id" in last_message.content:
            return {
                "messages": [AIMessage(content="✅ Quote ready! Send via WhatsApp? Reply 'send'")]
            }
        return {
            "messages": [AIMessage(content="✅ CRM operation completed!")]
        }
    
    return {"messages": [llm_with_tools.invoke(messages)]}

# Router
def route_crm(state: AgentState):
    last_message = state["messages"][-1]
    return "tools" if last_message.tool_calls else END

# 🛠️ BUILD GRAPH
workflow = StateGraph(AgentState)
workflow.add_node("parser", crm_parser)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("agent", agent_node)

workflow.set_entry_point("parser")
workflow.add_conditional_edges("parser", route_crm, {"tools": "tools", "__end__": END})
workflow.add_conditional_edges("tools", tools_condition, {"agent": "agent", "__end__": END})
workflow.add_edge("agent", END)

crm_graph = workflow.compile()  # ✅ No recursion_limit needed

def run_crm_agent(user_input: str):
    """Run agent."""
    result = crm_graph.invoke({"messages": [HumanMessage(content=user_input)]})
    return result["messages"][-1].content

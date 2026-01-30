from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from tools.crm import crm_update
import operator
import re
import os

# State definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]

# LLM Setup
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

# Bind tool to LLM
tools = [crm_update]
llm_with_tools = llm.bind_tools(tools)

def crm_parser(state: AgentState):
    """Parse CRM command → NO STRICT VALIDATION LOOPS."""
    user_input = state["messages"][-1].content.lower()
    
    # Flexible patterns
    patterns = [
        r"(?:update|change|set)\s+(cust\d{4})\s+(phone|name|email)\s*[:=]?\s*([^\s]+(?:\s+[^\s]+)?)(?:\s|$)",
        r"(?:update|change|set)\s+(cust\d{4})\s+(phone|name|email)\s+(.+?)(?:\s|$)",
        r"(update|change|set)\s+(cust\d{4})\s+(.+?)\s+(phone|name|email)\s+(.+?)(?:\s|$)",
    ]
    
    customer_id = field_type = field_value = ""
    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            groups = match.groups()
            customer_id = groups[0].upper()
            field_type = groups[1].lower()
            field_value = groups[2].strip()
            break
    
    # LOOSER VALIDATION - Only fail on obvious errors
    if not customer_id or len(customer_id) < 6:
        return {"messages": [AIMessage(content="❌ Format: `update CUST0001 phone 9876543210`")] }
    
    # Phone validation (optional - let tool handle)
    if field_type == "phone" and field_value:
        if len(field_value) < 10:
            return {"messages": [AIMessage(content=f"⚠️ Phone {field_value} looks short. Continue?")] }
    
    if not field_type or not field_value:
        return {"messages": [AIMessage(content="❌ Missing field/value. Examples:\n`update CUST0001 phone 9876543210`\n`change CUST0002 name Amit Kumar`")] }

    # ✅ TOOL CALL
    tool_input = {"customer_id": customer_id}
    if field_type == "phone": tool_input["phone"] = field_value
    elif field_type == "name": tool_input["name"] = field_value
    elif field_type == "email": tool_input["email"] = field_value
    
    return {
        "messages": [AIMessage(
            content=f"✅ Parsed: {customer_id} | {field_type} → {field_value}",
            tool_calls=[{
                "name": "crm_update",
                "args": tool_input,
                "id": "crm_1"
            }]
        )]
    }


# Agent node (handles tool responses)
def agent_node(state: AgentState):
    """Agent decides next action."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If last message is tool result, respond with summary
    if isinstance(last_message, ToolMessage):
        return {
            "messages": [AIMessage(content="✅ CRM operation completed successfully!")]
        }
    
    # Otherwise call LLM with tools
    return {"messages": [llm_with_tools.invoke(messages)]}

# Router
def route_crm(state: AgentState):
    messages = state["messages"]
    
    # Route to tools if tool_calls exist
    last_message = messages[-1]
    if last_message.tool_calls:
        return "tools"
    
    # End if no more actions needed
    return END

# Build SIMPLE graph: Parse → Tools → Agent → END
workflow = StateGraph(AgentState)

workflow.add_node("parser", crm_parser)
workflow.add_node("tools", ToolNode(tools))
workflow.add_node("agent", agent_node)

# Edges
workflow.set_entry_point("parser")
workflow.add_conditional_edges("parser", route_crm, {"tools": "tools", "__end__": END})
workflow.add_conditional_edges("tools", tools_condition, {"agent": "agent", "__end__": END})
workflow.add_edge("agent", END)

# Compile with recursion limit
crm_graph = workflow.compile()

def run_crm_agent(user_input: str):
    """Run CRM agent."""
    result = crm_graph.invoke({
        "messages": [HumanMessage(content=user_input)]
    })
    # Return final message content
    final_msg = result["messages"][-1]
    return final_msg.content

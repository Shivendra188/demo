from typing import TypedDict, Annotated, Sequence
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
from langchain_core.tools import tool
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode, tools_condition
from tools.crm import crm_update
import operator
import re

# State definition
class AgentState(TypedDict):
    messages: Annotated[Sequence[BaseMessage], operator.add]
    customer_id: str
    field_type: str
    field_value: str
    is_valid: bool

# LLM with tools
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
llm_with_tools = llm.bind_tools([crm_update])

# Nodes
def parse_command(state: AgentState):
    """Parse user input to extract customer_id, field, and value."""
    user_input = state["messages"][-1].content
    
    # Parse patterns
    patterns = {
        r"(?:update|change|set)\s+(CUST\d+)\s+(phone|name|email)\s+(.+?)(?:\s|$)",
        r"(?:update|change|set)\s+(CUST\d+)\s+(.+?)\s+to\s+(.+?)(?:\s|$)",
        r"update\s+(CUST\d+)\s+(phone|name|email)\s*=?\s*(.+?)(?:\s|$)"
    }
    
    customer_id = field_type = field_value = ""
    for pattern in patterns:
        match = re.search(pattern, user_input, re.IGNORECASE)
        if match:
            customer_id, field_type, field_value = match.groups()
            break
    
    # Validate phone format
    if field_type == "phone":
        phone_digits = re.sub(r'[^\d]', '', field_value)
        is_valid_phone = len(phone_digits) == 10 or field_value.startswith("+91")
        if not is_valid_phone:
            return {
                "messages": [HumanMessage(content=f"❌ Invalid phone format: {field_value}. Use 10 digits or +91xxxxxxxxxx")],
                "is_valid": False
            }
    
    # Validate customer_id format
    if not customer_id.startswith("CUST"):
        return {
            "messages": [HumanMessage(content="❌ Please use CUSTXXXX format (e.g., CUST0001)")],
            "is_valid": False
        }
    
    return {
        "messages": [AIMessage(content=f"✅ Parsed: Update {customer_id} {field_type} to '{field_value}'")],
        "customer_id": customer_id,
        "field_type": field_type,
        "field_value": field_value,
        "is_valid": True
    }

def call_tool(state: AgentState):
    """Call CRM update tool with parsed data."""
    if not state.get("is_valid"):
        return {"messages": [AIMessage(content="❌ Skipping tool call - invalid input")]}
    
    # Create tool input
    tool_input = {"customer_id": state["customer_id"]}
    if state["field_type"] == "phone":
        tool_input["phone"] = state["field_value"]
    elif state["field_type"] == "name":
        tool_input["name"] = state["field_value"]
    elif state["field_type"] == "email":
        tool_input["email"] = state["field_value"]
    
    # Generate tool call message
    tool_message = AIMessage(content="", tool_calls=[{
        "name": "crm_update",
        "args": tool_input,
        "id": "crm_update_call"
    }])
    
    return {"messages": [tool_message]}

def should_continue(state: AgentState):
    """Router function for graph flow."""
    messages = state["messages"]
    last_message = messages[-1]
    
    # If tool call made, continue to tool node
    if last_message.tool_calls:
        return "tools"
    
    # If invalid or complete, end
    if not state.get("is_valid", True):
        return END
    
    # Otherwise continue parsing
    return "parse"

# Router node
def router(state: AgentState):
    return should_continue(state)

# Build the graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("parse", parse_command)
workflow.add_node("agent", lambda state: {"messages": [llm_with_tools.invoke(state["messages"])]})
workflow.add_node("tools", ToolNode([crm_update]))

# Set entry point
workflow.set_entry_point("parse")

# Add edges
workflow.add_conditional_edges(
    "parse",
    router,
    {
        "parse": "parse",
        "tools": "tools",
        "agent": "agent"
    }
)
workflow.add_conditional_edges(
    "agent",
    tools_condition,
    {
        "tools": "tools",
        "__end__": END
    }
)
workflow.add_edge("tools", END)

# Compile graph
crm_graph = workflow.compile()

def run_crm_agent(user_input: str):
    """Run the CRM LangGraph agent."""
    result = crm_graph.invoke({
        "messages": [HumanMessage(content=user_input)]
    })
    return result["messages"][-1].content

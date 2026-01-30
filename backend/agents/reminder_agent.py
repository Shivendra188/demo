from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from langchain_core.tools import tool
from tools.reminder import reminder_tool  # Your existing tool
import os

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.1
)

# Simple Tool Calling Chain (NO AGENT NEEDED)
prompt = ChatPromptTemplate.from_messages([
    ("system", """Reminder Agent – insurance renewal expert.

Parse & act:
• "send reminders" → reminder_tool()
• "reminder CUST0001" → reminder_tool("CUST0001")
• ALWAYS call tool if renewal/expiring/Whatsapp mentioned

Respond friendly after tool."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
])

# Bind tool to Groq
llm_with_tools = llm.bind_tools([reminder_tool])

# Simple invoke chain
async def run_reminder_agent(user_input: str, chat_history: list = []):
    messages = chat_history + [HumanMessage(content=user_input)]
    
    # Groq tool call
    response = await llm_with_tools.ainvoke(messages)
    
    # Execute tool if called
    if response.tool_calls:
        tool_result = reminder_tool.invoke(response.tool_calls[0]["args"])
        tool_msg = ToolMessage(
            content=tool_result,
            tool_call_id=response.tool_calls[0]["id"]
        )
        
        # Final response
        final_response = await llm.ainvoke(messages + [response, tool_msg])
        return {
            "response": final_response.content,
            "tool_used": True,
            "result": tool_result
        }
    
    # No tool needed
    return {
        "response": response.content,
        "tool_used": False
    }

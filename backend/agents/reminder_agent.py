import os
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.messages import HumanMessage, ToolMessage
from tools.reminder import reminder_tool


# ======================
# LLM (Groq only)
# ======================
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant",
    temperature=0.1,
)

# ======================
# Prompt
# ======================
prompt = ChatPromptTemplate.from_messages([
    ("system", """
You are Reminder Agent – an insurance renewal automation expert.

Rules:
• If message mentions reminder / renewal / expiry / WhatsApp → CALL reminder_tool
• "send reminders" → reminder_tool()
• "reminder CUST0001" → reminder_tool(customer_id="CUST0001")
• After tool execution, reply politely with confirmation
"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}")
])

# ======================
# Bind tool
# ======================
llm_with_tools = llm.bind_tools([reminder_tool])


# ======================
# Agent Runner
# ======================
async def run_reminder_agent(user_input: str, chat_history: list | None = None):
    chat_history = chat_history or []

    # Build prompt messages
    chain = prompt | llm_with_tools
    response = await chain.ainvoke({
        "input": user_input,
        "chat_history": chat_history
    })

    # Tool execution
    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_output = reminder_tool.invoke(tool_call["args"])

        tool_msg = ToolMessage(
            content=str(tool_output),
            tool_call_id=tool_call["id"]
        )

        final = await llm.ainvoke([
            *chat_history,
            HumanMessage(content=user_input),
            response,
            tool_msg
        ])

        return {
            "agent": "Reminder Agent",
            "response": final.content,
            "tool_used": True,
            "result": tool_output
        }

    # No tool call
    return {
        "agent": "Reminder Agent",
        "response": response.content,
        "tool_used": False
    }

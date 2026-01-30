from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from langchain_core.messages import HumanMessage
from tools.reminder import reminder_tool
import os 

llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)
prompt = ChatPromptTemplate.from_messages([
    ("system", """You are Reminder Agent – expert at insurance renewals.

When to act:
• "reminder", "renewal", "expiring", "whatsapp" → Send WhatsApp
• customer_id → Single targeted reminder
• No ID → Batch all expiring (30 days)

ALWAYS call reminder_tool. Confirm before sending.
Examples:
"send reminders" → Batch all
"reminder CUST0001" → Single customer"""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

# Create agent
agent = create_openai_functions_agent(llm, [reminder_tool], prompt)
agent_executor = AgentExecutor(agent=agent, tools=[reminder_tool], verbose=True)

def run_reminder_agent(user_input: str, chat_history: list = []):
    """Run reminder agent."""
    result = agent_executor.invoke({
        "input": user_input,
        "chat_history": chat_history
    })
    return result["output"]

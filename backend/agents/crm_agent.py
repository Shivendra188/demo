from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.agents import create_openai_functions_agent, AgentExecutor
from tools.crm import crm_update

llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

prompt = ChatPromptTemplate.from_messages([
    ("system", """You are CRM Agent – expert at customer data updates.

Parse commands like:
• "update CUST0001 phone 9876543210"
• "change CUST0002 name Amit Kumar"
• "set CUST0003 email amit@email.com"

ALWAYS:
1. Extract customer_id (CUSTXXXX)
2. Identify field (phone/name/email) + value
3. Validate phone format (+91 or 10 digits)
4. Call crm_update tool
5. Confirm changes

NEVER guess IDs. Ask if unclear."""),
    MessagesPlaceholder(variable_name="chat_history", optional=True),
    ("human", "{input}"),
    MessagesPlaceholder(variable_name="agent_scratchpad"),
])

agent = create_openai_functions_agent(llm, [crm_update], prompt)
crm_executor = AgentExecutor(agent=agent, tools=[crm_update], verbose=True)

def run_crm_agent(user_input: str):
    result = crm_executor.invoke({"input": user_input})
    return result["output"]

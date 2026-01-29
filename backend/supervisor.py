import os
from dotenv import load_dotenv

from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq

load_dotenv()

llm = ChatGroq(
    api_key=os.getenv("GROQ_API_KEY")    
    ,
    model_name="llama-3.1-8b-instant"   
)

prompt = PromptTemplate(
    input_variables=["query"],
    template="""
You are a supervisor AI for insurance operations. Classify the user's request into ONE category:
- QUOTE → asking for new insurance options or pricing
- POLICY → asking about an existing policy or its details
- REMINDER → asking about renewal, expiry, or notifications
- CRM → asking to update customer details or contact info

Examples:
- "Can I get a health insurance quote?" → QUOTE
- "When does my car policy expire?" → REMINDER
- "Update my phone number to 9876543210" → CRM
- "Show me details of policy POL123" → POLICY

User input: {query}

Reply with only ONE word from the list above.
"""
)


def route_task(user_input: str) -> str:
    response = llm.invoke(prompt.format(query=user_input))
    return response.content.strip().upper()


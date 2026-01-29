from langchain_core.prompts import PromptTemplate
from langchain_groq import ChatGroq
from services.pdf_parser import read_policy_pdf

# Load policy text once (fast)
POLICY_TEXT = read_policy_pdf(
    "policy.pdf"
)

llm = ChatGroq(
    api_key="sk_test_XXXXXXXXXXXXXXXXXXXXXX",
    model="llama-3.1-70b-versatile"
)

POLICY_PROMPT = PromptTemplate(
    input_variables=["question", "policy_text"],
    template="""
You are a professional insurance policy assistant.

Answer the question strictly using the policy document below.
If the answer is not present, say:
"I could not find this information in the policy document."

POLICY DOCUMENT:
{policy_text}

QUESTION:
{question}

ANSWER:
"""
)

def handle_policy_query(user_question: str) -> str:
    prompt = POLICY_PROMPT.format(
        question=user_question,
        policy_text=POLICY_TEXT
    )

    response = llm.invoke(prompt)
    return response.content

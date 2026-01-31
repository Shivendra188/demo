import os
from typing import Optional
from langchain_groq import ChatGroq

# =========================
# LOAD GROQ API KEY
# =========================
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================
# INITIALIZE LLM SAFELY
# =========================
llm: Optional[ChatGroq] = None

if GROQ_API_KEY:
    try:
        llm = ChatGroq(
            api_key=GROQ_API_KEY,
            model="llama-3.1-8b-instant",
            temperature=0.2,
            max_tokens=400,
        )
    except Exception:
        llm = None

# =========================
# MAIN POLICY AGENT
# (REQUIRED BY supervisor.py)
# =========================
def handle_policy_query(user_input: str) -> str:
    """
    Handles insurance policy-related questions such as:
    coverage, benefits, claims, renewal, exclusions, etc.
    """

    # ---------- API key missing or model init failed ----------
    if llm is None:
        return (
            "Policy information service is temporarily unavailable. "
            "Please try again later."
        )

    # ---------- Empty input safety ----------
    if not user_input or not user_input.strip():
        return "Please ask a valid policy-related question."

    try:
        response = llm.invoke(
            f"""
You are an insurance policy assistant.

Answer the user's question clearly and briefly.
Avoid legal jargon.
Keep the answer short and helpful.

User question:
{user_input}

Limit the response to a maximum of 4 lines.
"""
        )

        # LangChain safety: ensure content exists
        if hasattr(response, "content") and response.content:
            return response.content.strip()

        return "I couldn't generate a response for your policy question."

    # ---------- Any Groq / LangChain failure ----------
    except Exception:
        return (
            "Sorry, I’m unable to answer your policy question right now. "
            "Please try again later."
        )

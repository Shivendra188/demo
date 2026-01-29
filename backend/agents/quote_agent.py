from typing import Dict
from langchain_groq import ChatGroq
import os

# LLM only for explanation (NOT calculation)
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="llama-3.1-8b-instant"
)

def calculate_premium(age: int, coverage: int) -> int:
    # Base premium by age
    if age < 30:
        base = 4000
    elif age <= 45:
        base = 6000
    else:
        base = 9000

    # Coverage multiplier
    if coverage <= 5:
        multiplier = 1
    elif coverage <= 10:
        multiplier = 1.7
    else:
        multiplier = 3

    return int(base * multiplier)

def generate_quote(payload: Dict):
    age = payload.get("age", 30)
    coverage = payload.get("coverage_lakh", 5)
    duration = payload.get("duration_years", 1)

    premium = calculate_premium(age, coverage)

    explanation_prompt = f"""
    Explain this insurance quote in simple terms:

    Age: {age}
    Coverage: ₹{coverage} lakh
    Duration: {duration} year(s)
    Annual Premium: ₹{premium}

    Keep it friendly and clear.
    """

    explanation = llm.invoke(explanation_prompt).content

    return {
        "type": "QUOTE",
        "age": age,
        "coverage_lakh": coverage,
        "duration_years": duration,
        "annual_premium": premium,
        "explanation": explanation
    }

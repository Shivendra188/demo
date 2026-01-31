import re
import os
import pdfplumber
from typing import Dict, Optional
from groq import APIStatusError
from langchain_groq import ChatGroq

# =========================
# CONFIG
# =========================
PDF_PATH = os.path.join("data", "policies.pdf")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# =========================
# LLM (SAFE INIT)
# =========================
llm = None
if GROQ_API_KEY:
    llm = ChatGroq(
        api_key=GROQ_API_KEY,
        model="llama-3.1-8b-instant",
        temperature=0.2,
        max_tokens=300,
    )

# =========================
# GLOBAL CACHE (IMPORTANT)
# =========================
POLICY_STORE: Optional[Dict[str, Dict]] = None


# =========================
# LOAD POLICIES FROM PDF
# =========================
def load_policies_from_pdf(pdf_path: str) -> Dict[str, Dict]:
    policies: Dict[str, Dict] = {}

    if not os.path.exists(pdf_path):
        print("[POLICY_DATA] policies.pdf not found")
        return policies

    # 1️⃣ Read full PDF text
    with pdfplumber.open(pdf_path) as pdf:
        full_text = ""
        for page in pdf.pages:
            text = page.extract_text()
            if text:
                full_text += " " + text

    # 2️⃣ Normalize whitespace
    full_text = re.sub(r"\s+", " ", full_text)

    # 3️⃣ Robust regex for policy rows
    pattern = re.compile(
        r"(POL\d{4})\s+"                   # Policy ID
        r"\w+\s+"                          # Customer ID (ignored)
        r"(Health|Life|Vehicle)\s+"        # Policy Type
        r"(.*?)\s+"                        # Insurer
        r"(\d{4,6})\s+"                    # Premium
        r"(\d{2}-\d{2}-\d{2})\s+"          # Start Date
        r"(\d{2}-\d{2}-\d{2})\s+"          # Expiry Date
        r"(Active|Expired|Expiring)\s+"    # Status
        r"([A-Za-z ]+)"                    # Customer Name
    )

    for match in pattern.finditer(full_text):
        policy_id = match.group(1)

        policies[policy_id] = {
            "policy_id": policy_id,
            "policy_type": match.group(2),
            "insurer": match.group(3).strip(),
            "premium": int(match.group(4)),
            "start_date": match.group(5),
            "expiry_date": match.group(6),
            "status": match.group(7),
            "customer_name": match.group(8).strip(),
        }

    print(f"[POLICY_DATA] Loaded {len(policies)} policies from PDF")
    return policies


# =========================
# UTILS
# =========================
def extract_policy_number(text: str) -> Optional[str]:
    match = re.search(r"\bPOL\d{4}\b", text.upper())
    return match.group(0) if match else None


# =========================
# MAIN AGENT
# =========================
def handle_policy_data_query(user_input: str) -> str:
    global POLICY_STORE

    # 🔥 Lazy-load PDF (fixes Windows reload crash)
    if POLICY_STORE is None:
        POLICY_STORE = load_policies_from_pdf(PDF_PATH)

    policy_number = extract_policy_number(user_input)

    if not policy_number:
        return "Please provide a valid policy number (e.g., POL1025)."

    policy = POLICY_STORE.get(policy_number)

    if not policy:
        return f"No policy found with number {policy_number}."

    text = user_input.lower()

    # ---------- FAST FACTUAL ANSWERS ----------
    if any(k in text for k in ["status", "expire", "expiry"]):
        return (
            f"Policy {policy_number} is **{policy['status']}** "
            f"and expires on **{policy['expiry_date']}**."
        )

    if "premium" in text or "price" in text:
        return f"The premium for policy {policy_number} is ₹{policy['premium']}."

    if "owner" in text or "customer" in text or "name" in text:
        return f"Policy {policy_number} belongs to {policy['customer_name']}."

    # ---------- AI SUMMARY ----------
    if llm is None:
        return (
            f"Policy {policy_number} is a {policy['policy_type']} policy "
            f"issued by {policy['insurer']}."
        )

    try:
        response = llm.invoke(
            f"""
Policy details:
{policy}

User question:
{user_input}

Answer briefly (max 4 lines).
"""
        )
        return response.content.strip()

    except APIStatusError:
        return "Unable to summarize policy right now. Please try again."

    except Exception:
        return "Something went wrong while processing the policy."

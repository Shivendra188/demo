🤖 Insurance AI Copilot (Multi-Agent System)

An AI-powered Insurance Copilot that enables users to interact with insurance systems using natural language.
The system intelligently routes requests to specialized AI agents for Quotes, Policy Queries, CRM Updates, and WhatsApp Reminders.

Designed for hackathons, demos, and real-world fintech / insurtech use cases.

🚀 Features
🧠 Multi-Agent Architecture

Supervisor Agent
Detects user intent and routes the request to the correct agent

Quote Agent
Generates insurance quotes based on user input

Policy Agent
Answers questions from insurance policy documents (PDF-based)

CRM Agent
Updates and retrieves customer data using natural language commands

Reminder Agent
Sends WhatsApp renewal reminders automatically

💬 AI Copilot Chat Interface

Chat-style UI (ChatGPT-like experience)

Displays which agent handled the request

Real-time agent status panel

Live activity feed for system actions and updates

📊 CRM Dashboard

View customers and their policies

Policy status tracking: Active / Expired

Auto-refreshing customer table

Backend-driven, real-time data updates

🏗️ Tech Stack
🔹 Backend

FastAPI (Python)

LangChain + LangGraph

Groq LLM (llama-3.1-8b-instant)

Supabase (PostgreSQL)

Twilio WhatsApp API

PyMuPDF (PDF parsing)

🔹 Frontend

React + Vite

Axios

Tailwind CSS

Component-based UI architecture

📂 Project Structure
hackjnu/
├── backend/
│   ├── main.py
│   ├── agents/
│   │   ├── supervisor.py
│   │   ├── quote_agent.py
│   │   ├── policy_agent.py
│   │   ├── crm_agent.py
│   │   └── reminder_agent.py
│   ├── services/
│   │   ├── whatsapp.py
│   │   └── pdf_parser.py
│   ├── tools/
│   │   ├── crm.py
│   │   └── reminder.py
│   └── .env
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── CopilotChat.jsx
│   │   │   ├── CustomerTable.jsx
│   │   │   ├── ActivityFeed.jsx
│   │   │   └── AgentsStatus.jsx
│   │   ├── services/api.js
│   │   └── App.jsx
│   └── .env
│
└── README.md

🔌 Backend API Endpoints
🔹 AI Copilot Chat

POST /chat

Request

{
  "message": "policy POL1001"
}


Response

{
  "agent": "Policy Agent",
  "response": "This policy covers hospitalization up to ₹5L..."
}

🔹 CRM Dashboard

GET /crm-dashboard

Response

{
  "data": [
    {
      "name": "Rahul Sharma",
      "phone": "9876543210",
      "policy_type": "Health",
      "policy_id": "POL1001",
      "status": "Active"
    }
  ],
  "total": 1,
  "updated": "2026-01-30"
}

⚙️ Environment Variables
Backend (backend/.env)
GROQ_API_KEY=your_groq_key
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_supabase_key
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886

Frontend (frontend/.env)
VITE_API_BASE_URL=http://127.0.0.1:8000


🚨 Never hardcode secrets — GitHub push protection is enabled.

▶️ Running the Project
1️⃣ Backend
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload


Backend runs at:
👉 http://127.0.0.1:8000

2️⃣ Frontend
cd frontend
npm install
npm run dev


Frontend runs at:
👉 http://localhost:5173

🧪 Example Commands to Try
health quote CUST0001
policy POL1001
send reminders
update CUST0001 phone 9876543210

You’ll See:

Active agent highlighted

AI response in chat

Activity feed updated in real time

CRM table refreshed automatically

🧠 System Design (High Level)
User → Frontend Chat
     → POST /chat
     → Supervisor Agent
     → Specialized Agent
     → Backend Response
     → Frontend UI + Activity Feed

🔐 Security Best Practices

✅ Secrets stored in environment variables

✅ No API keys exposed in frontend

✅ GitHub secret scanning enabled

✅ Centralized backend request routing

🌟 Future Enhancements

Policy RAG using embeddings + vector database

WebSocket-based live activity feed

Agent confidence scoring

Voice input for the Copilot

Role-based dashboards (Admin / Agent / Customer)

👨‍💻 Author

Shivendra
Insurance AI Copilot – HackJNU Project

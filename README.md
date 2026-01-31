# Insurance AI Copilot (Multi-Agent System)

An AI-powered Insurance Copilot that enables users to interact with insurance systems using natural language.
The system intelligently routes requests to specialized AI agents for Quotes, Policy Queries, CRM Updates, and WhatsApp Reminders.
<img width="1327" height="831" alt="image" src="https://github.com/user-attachments/assets/2ff8e525-2023-4ce2-9f79-0da095cad3f7" />
```
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
```

Environment Variables
```
Backend (backend/.env)
GROQ_API_KEY=your_groq_key
SUPABASE_URL=https://xxxx.supabase.co
SUPABASE_KEY=your_supabase_key
TWILIO_ACCOUNT_SID=ACxxxx
TWILIO_AUTH_TOKEN=xxxx
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```
Frontend (frontend/.env)
VITE_API_BASE_URL=http://127.0.0.1:8000

# Running the Project
Backend
```
cd backend
python -m venv venv
venv\Scripts\activate     # Windows
pip install -r requirements.txt
uvicorn main:app --reload
```
Backend runs at:
- http://127.0.0.1:8000

Frontend
```
cd frontend
npm install
npm run dev
```
Frontend runs at:
- http://localhost:5173

Example Commands to Try in the prompting area
- health quote CUST0001
- policy POL1001
- send reminders
- update CUST0001 phone 9876543210

# System Design (High Level)
```
User → Frontend Chat
     → POST /chat
     → Supervisor Agent
     → Specialized Agent
     → Backend Response
     → Frontend UI + Activity Feed
```

Future Enhancements
- Policy RAG using embeddings + vector database
- WebSocket-based live activity feed
- Agent confidence scoring
- Voice input for the Copilot
- Role-based dashboards (Admin / Agent / Customer)

Team AlgoGen

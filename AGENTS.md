# AGENTS.md

This file provides guidance to WARP (warp.dev) when working with code in this repository.

## Project Overview

This is an Insurance AI Copilot application with a multi-agent LangChain/LangGraph architecture. The system uses a supervisor agent to route user queries to specialized agents (Quote, Policy, CRM, Reminder) that interact with Supabase for data storage and Twilio for WhatsApp notifications.

**Architecture:**
- **Backend**: FastAPI + Python (LangChain/LangGraph agents)
- **Frontend**: React 19 + Vite + TailwindCSS
- **Database**: Supabase (customers, policies, quotes tables)
- **External Services**: Twilio WhatsApp, Groq LLM API

## Development Commands

### Backend (Python FastAPI)

```powershell
# Setup virtual environment (first time only)
cd backend
python -m venv venv
venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run backend server (with auto-reload)
uvicorn main:app --reload

# Backend runs on http://localhost:8000
```

**Important**: The backend requires a `.env` file in the `backend/` directory with:
- `GROQ_API_KEY` - For LLM inference
- `ACC_SID`, `AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER` - For WhatsApp messaging
- `SUPABASE_URL`, `SUPABASE_KEY` - For database access

### Frontend (React + Vite)

```powershell
# Install dependencies
cd frontend
npm install

# Run development server
npm run dev

# Build for production
npm run build

# Lint code
npm run lint

# Preview production build
npm run preview

# Frontend runs on http://localhost:5173
```

## Architecture Details

### Backend Agent System

The backend uses a **supervisor pattern** where user queries are routed to specialized agents:

**Agent Flow:**
1. User message → `/chat` endpoint in `backend/main.py`
2. `agents/supervisor.py` → Routes based on keywords to determine task type (QUOTE/POLICY/CRM/REMINDER)
3. Specialized agent executes task using tools and returns response

**Agents:**
- `agents/supervisor.py` - Routes queries to appropriate agent based on keyword matching
- `agents/quote_agent.py` - Generates insurance quotes using age/coverage calculations + LLM explanations
- `agents/policy_agent.py` - Handles policy queries, may use RAG on `policy.pdf` for detailed coverage info
- `agents/crm_agent.py` - Updates customer records in Supabase
- `agents/reminder_agent.py` - Sends WhatsApp reminders for expiring policies (<30 days)

**Tools:** Located in `backend/tools/`, tools provide agent capabilities (e.g., `policy.py` for policy lookups)

**Services:**
- `services/whatsapp.py` - Twilio WhatsApp integration using `send_whatsapp_message()`

### Supabase Database Schema

The application expects these tables:
- **customers**: `customer_id`, `name`, `phone`, `email`
- **policies**: `policy_id`, `customer_id`, `policy_type` (Health/Car/Life), `policy_expiry`, `premium`, `status`
- **quotes**: `quote_id`, `policy_type`, `insurer`, `coverage_amount`, `premium`, `deductible`

### Backend API Endpoints

- `POST /chat` - Main chat interface, routes to agents
- `GET /crm-dashboard` - Returns policies with customer data for dashboard
- `GET /customers` - List customers (limit param)
- `GET /policies` - List policies (limit param)
- `GET /expiring` - Policies expiring before 2026-02-28
- `POST /send-reminder` - Send single WhatsApp reminder
- `POST /batch-reminders` - Send bulk reminders to expiring policies

### Frontend Structure

**Components:** (`frontend/src/components/`)
- `Sidebar.jsx` - Navigation sidebar
- `CopilotChat.jsx` - Main chat interface for agent interaction
- `CustomerTable.jsx` - CRM dashboard showing customer/policy data
- `AgentsStatus.jsx` - Agent status monitoring
- `ActivityFeed.jsx` - Activity log

**Routing:** React Router v7 with routes: `/chat`, `/customers`, `/agents`, `/activity`

**Styling:** TailwindCSS v4 configured via Vite plugin

## Important Implementation Notes

### Environment Variables
Always use `os.getenv()` with the `python-dotenv` package. Never hardcode credentials. The backend loads `.env` via `load_dotenv()` in `main.py`.

### Agent Development
- Supervisor uses simple keyword matching (not semantic) - keywords defined in `route_task()`
- Quote agent uses deterministic calculation (`calculate_premium()`) + LLM for explanations
- Agents return structured responses with `{"agent": str, "type": str, "response": dict}`

### Supabase Queries
- Use `supabase.table(name).select().execute().data` pattern
- Join syntax: `.select("*, customers(name, phone)")` for foreign key relations
- The Supabase client is initialized in `main.py` with environment variables

### WhatsApp Integration
- Uses Twilio sandbox: `whatsapp:+14155238886` as sender
- Recipient format: `whatsapp:+[country_code][number]`
- Message format includes "Insurance Copilot\n" prefix

## Testing Chat Examples

Example queries to test each agent:

```json
{"message": "What benefits are covered in policy POL1001?"}
{"message": "health quote for 30 year old"}
{"message": "update customer CUST0001 phone 9876543210"}
{"message": "send renewal reminders"}
{"message": "show me life insurance plans"}
```

## Tech Stack Versions

- React: 19.2.0
- Vite: 7.3.1
- TailwindCSS: 4.1.18
- FastAPI: latest (via requirements.txt)
- LangChain + langchain-groq: latest
- Python: 3.x (venv required)

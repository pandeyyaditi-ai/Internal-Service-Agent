<<<<<<< HEAD
# Internal Service Agent 🤖

> **Enterprise AI-Powered IT Helpdesk Agent**  
> An intelligent support agent designed to resolve internal employee technical queries, diagnose VPN issues, answer IT FAQs with citations, handle ticket lifecycle (CRUD), and automatically escalate unresolved or critical incidents to human IT engineers.

---

## 🌟 Key Features

1. **Intelligent Conversational Agent**
   - Natural language comprehension with Google Gemini Pro and robust keyword fallback.
   - Handles multi-turn conversations with contextual awareness and persistent session tracking.

2. **Automated Intent Detection & Routing**
   - Classifies inquiries into: `vpn_issue`, `faq`, `ticket_request`, `escalation`, and `general`.
   - Dispatches requests directly to dedicated resolution handlers.

3. **Step-by-Step VPN Diagnostic Engine**
   - Interactive troubleshooting workflow verifying credentials, GlobalProtect client status, DNS/gateways, and firewall rules.

4. **Knowledge Base & Policy Retrieval**
   - Comprehensive repository of IT policies and FAQs with exact source referencing and relevance scoring.

5. **Full Ticket Lifecycle Management**
   - Instant ticket generation, auto-priority classification (Critical/High/Medium/Low), category auto-detection, status tracking, and notes.

6. **Smart Escalation Matrix**
   - Automated escalation triggers on low model confidence (< 0.4), explicit user request ("talk to human"), multiple failed resolution attempts (>= 3), or critical priority incidents.

7. **Compliance & Audit Logging**
   - Immutable audit trail recording every user inquiry, agent action, classification, escalation, and ticket state modification.

8. **Executive Dashboard & Realtime UI**
   - Real-time WebSocket chat, SLA metrics, open ticket stats, escalation alerts, and responsive dark-theme glassmorphism interface.

---

## 🏗️ Architecture

```
internal_service_agent/
│
├── backend/
│   ├── app/
│   │   ├── api/                 # FastAPI REST & WebSocket routers
│   │   │   ├── chat_routes.py   # Chat & WebSocket endpoints
│   │   │   ├── ticket_routes.py # Ticket CRUD & stats
│   │   │   ├── audit_routes.py  # Audit trail inspection
│   │   │   └── routes.py        # Master API router
│   │   ├── core/                # Config, logging, security
│   │   ├── database/            # Motor async MongoDB client & seeder
│   │   ├── knowledge_base/      # IT FAQs (JSON) & policy documents
│   │   ├── models/              # Pydantic & database domain models
│   │   ├── schemas/             # Request/response schemas
│   │   ├── services/            # Intent classification, troubleshooting, escalation
│   │   ├── utils/               # DateTime and validation helpers
│   │   └── main.py              # Application entry point
│   ├── tests/                   # Pytest suite
│   ├── requirements.txt
│   └── .env
│
└── frontend/
    ├── public/                  # Static assets & index.html
    └── src/
        ├── components/          # Reusable UI widgets (ChatWindow, TicketCard, etc.)
        ├── pages/               # Dashboard, SupportChat, Tickets, AuditTrail
        ├── services/            # API client (Fetch / Axios wrapper)
        ├── hooks/               # useChat WebSocket hook
        ├── utils/               # Date & label formatters
        └── styles/              # Dark glassmorphic design system CSS
```

---

## 🚀 Quick Start

### 1. Backend Setup

```bash
cd backend
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate

pip install -r requirements.txt
```

Configure `backend/.env`:
```env
APP_NAME=Internal Service Agent
APP_VERSION=1.0.0
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=internal_service_agent
GEMINI_API_KEY=your_gemini_api_key_here
LOG_LEVEL=INFO
CORS_ORIGINS=["http://localhost:3000","http://localhost:5173"]
```

Run database seeder and backend server:
```bash
uvicorn app.main:app --reload --port 8000
```
- Interactive Swagger docs: [http://localhost:8000/docs](http://localhost:8000/docs)
- Health check: [http://localhost:8000/health](http://localhost:8000/health)

Run unit tests:
```bash
pytest
```

---

### 2. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# or npm start depending on runner
```

Open [http://localhost:3000](http://localhost:3000) (or `http://localhost:5173`) in your browser.

---

## 📡 API Endpoints Overview

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/api/chat/message` | Send message to AI agent & get structured response |
| `GET` | `/api/chat/conversations/{emp_id}` | Retrieve past conversations for an employee |
| `GET` | `/api/chat/conversation/{conv_id}` | Get full conversation history |
| `WS` | `/api/chat/ws/{emp_id}` | Real-time WebSocket interactive chat |
| `GET` | `/api/tickets` | List tickets with category/status/priority filters |
| `POST` | `/api/tickets` | Create support ticket |
| `GET` | `/api/tickets/{ticket_id}` | Retrieve single ticket detail |
| `PUT` | `/api/tickets/{ticket_id}` | Update ticket status, resolution, or priority |
| `GET` | `/api/tickets/stats` | Retrieve dashboard KPI counts & metrics |
| `GET` | `/api/audit` | Query audit logs with pagination and filters |
| `GET` | `/api/health` | Service and database health status |

---

## 🛡️ Escalation Policies

- **Low Confidence**: Triggers escalation when intent classification confidence is `< 0.4`.
- **Repeated Unresolved Attempts**: Auto-escalates if troubleshooting loop fails after 3 attempts.
- **Priority Override**: Any ticket classified as `CRITICAL` triggers an automated escalation alert to the on-call engineer.
- **Explicit Request**: Direct human request keywords ("speak to human", "manager", "transfer me") immediately invoke escalation workflows.
=======
# Internal-Service-Agent
The Internal Service Agent acts as a virtual IT support assistant that helps employees solve routine IT problems, provides policy-based answers, and escalates complex issues to human support when required.

this is my full-stack structure:

Internal_Service_Agent/
│
├── frontend/
│   ├── index.html
│   ├── package.json
│   ├── public/
│   │   └── assets/
│   │       └── logo.png
│   │
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       │
│       ├── components/
│       │   ├── ChatWindow.jsx
│       │   ├── Message.jsx
│       │   ├── ChatInput.jsx
│       │   ├── TicketCard.jsx
│       │   ├── TicketStatus.jsx
│       │   ├── SourceReference.jsx
│       │   ├── EscalationAlert.jsx
│       │   └── Sidebar.jsx
│       │
│       ├── pages/
│       │   ├── Dashboard.jsx
│       │   ├── SupportChat.jsx
│       │   ├── Tickets.jsx
│       │   └── AuditTrail.jsx
│       │
│       ├── services/
│       │   └── api.js
│       │
│       ├── hooks/
│       │   └── useChat.js
│       │
│       ├── utils/
│       │   └── formatters.js
│       │
│       └── styles/
│           ├── App.css
│           ├── Chat.css
│           ├── Dashboard.css
│           └── Ticket.css
│
├── backend/
│   ├── requirements.txt
│   ├── .env
│   │
│   ├── app/
│   │   ├── main.py
│   │
│   │   ├── api/
│   │   │   ├── routes.py
│   │   │   ├── chat_routes.py
│   │   │   ├── ticket_routes.py
│   │   │   └── audit_routes.py
│   │   │
│   │   ├── models/
│   │   │   ├── employee.py
│   │   │   ├── ticket.py
│   │   │   ├── conversation.py
│   │   │   └── audit.py
│   │   │
│   │   ├── schemas/
│   │   │   ├── chat_schema.py
│   │   │   ├── ticket_schema.py
│   │   │   └── response_schema.py
│   │   │
│   │   ├── services/
│   │   │   ├── agent.py
│   │   │   ├── intent_detection.py
│   │   │   ├── policy_search.py
│   │   │   ├── troubleshooting.py
│   │   │   ├── ticket_service.py
│   │   │   ├── escalation.py
│   │   │   └── audit_service.py
│   │   │
│   │   ├── knowledge_base/
│   │   │   ├── policies/
│   │   │   │   ├── password_policy.pdf
│   │   │   │   ├── vpn_policy.pdf
│   │   │   │   ├── laptop_policy.pdf
│   │   │   │   └── software_installation_policy.pdf
│   │   │   │
│   │   │   └── faqs/
│   │   │       └── it_faq.json
│   │   │
│   │   ├── database/
│   │   │   ├── database.py
│   │   │   └── seed.py
│   │   │
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── security.py
│   │   │   └── logging.py
│   │   │
│   │   └── utils/
│   │       ├── date_utils.py
│   │       └── validators.py
│   │
│   └── tests/
│       ├── test_chat.py
│       ├── test_ticket.py
│       ├── test_escalation.py
│       └── test_policy_search.py
│
├── data/
│   ├── policies/
│   ├── faq/
│   └── sample_tickets/
│
├── README.md
└── .gitignore
>>>>>>> 8458495b29bf3a30900f481b0b36dc524306bbbc

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

# OMS Support

AI-powered customer support system for **Open Money Stack (OMS) by Polygon**.

Combines an always-on AI agent (Claude + RAG) with a structured human escalation hierarchy (L1 → L2 → L3) to serve end users, developers, and enterprise partners.

---

## Features

- **AI Agent (Tier 0)** — Claude Opus 4.6 with RAG over OMS docs. Targets 60–70% autonomous resolution.
- **Ticket management** — Freshdesk-compatible ticket lifecycle with SLA tracking and breach alerts.
- **Escalation workflows** — Structured L1 → L2 → L3 routing with configurable triggers.
- **Knowledge base** — ChromaDB-backed vector store ingesting OMS docs, resolved issues, and synthetic FAQs.
- **Analytics dashboard** — React admin UI with resolution rates, SLA compliance, and CSAT metrics.
- **Embeddable widget** — Drop-in React chat widget for any OMS-powered product.

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend API | FastAPI (Python) |
| AI Agent | Claude Opus 4.6 (Anthropic API) |
| Vector store | ChromaDB |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Database | SQLite / SQLAlchemy |
| Frontend | React 18, TypeScript, Vite |
| Charts | Recharts |

---

## Project Structure

```
oms-support/
├── backend/
│   ├── api/              # Route handlers (chat, tickets, feedback, analytics, knowledge)
│   ├── core/             # AI agent, RAG pipeline, escalation logic
│   ├── models/           # SQLAlchemy models
│   ├── knowledge/        # KB ingestion scripts
│   ├── config.py
│   ├── database.py
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   └── src/              # React admin dashboard + embeddable widget
├── docs/
│   ├── getting_started.md
│   └── faq.md
├── OMS_Support_Model.md  # Support model: sub-units, escalation matrix, SLAs
└── OMS_Technical_Deep_Dive.md
```

---

## Getting Started

### Backend

```bash
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # add your ANTHROPIC_API_KEY
uvicorn main:app --reload
```

API will be available at `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

Dashboard will be available at `http://localhost:5173`.

---

## Support Model

See [`OMS_Support_Model.md`](./OMS_Support_Model.md) for the full support model including:

- Sub-units and escalation matrix (L1/L2/L3)
- SLA targets and breach handling
- Severity classification (Critical / High / Medium / Low)
- Ticket resolution workflow
- Communication channels

---

## Documentation

- [Getting Started](./docs/getting_started.md)
- [FAQ](./docs/faq.md)
- [Technical Deep Dive](./OMS_Technical_Deep_Dive.md)

---

*Maintained by the Polygon OMS Team*

# OMS Support System — Technical Deep Dive
### Ticket Routing · AI Agent · Knowledge Base Pipeline
**Version 1.0 | May 2026**

---

## Overview

This document provides a detailed technical and operational breakdown of three core components of the OMS support system:

1. **Ticket Routing** — how incoming queries are classified, assigned to tiers, and tracked against SLAs
2. **AI Agent** — how the Tier 0 AI support agent works, what it can and cannot do, and how it decides to escalate
3. **Knowledge Base Pipeline** — how OMS documentation is ingested, stored, retrieved, and kept current

These three components are deeply interdependent. The KB Pipeline feeds the AI Agent with context. The AI Agent produces triage signals. The triage signals drive the Ticket Routing system.

```
┌──────────────────────────────────────────────────┐
│                  User Query                       │
└──────────────────┬───────────────────────────────┘
                   │
                   ▼
┌──────────────────────────────────────────────────┐
│         KB Pipeline (retrieval)                  │
│   Embeds query → searches ChromaDB → returns     │
│   top-k relevant document chunks                 │
└──────────────────┬───────────────────────────────┘
                   │  context chunks
                   ▼
┌──────────────────────────────────────────────────┐
│              AI Agent (Claude Opus 4.6)          │
│   RAG prompt → generates answer → emits          │
│   confidence score + intent classification       │
└──────────────────┬───────────────────────────────┘
                   │  triage metadata
                   ▼
┌──────────────────────────────────────────────────┐
│           Ticket Routing Engine                  │
│   Applies routing rules → assigns tier →         │
│   computes SLA deadline → creates ticket         │
└──────────────────────────────────────────────────┘
```

---

# Part 1: Ticket Routing

## 1.1 What is the Routing Engine?

The routing engine is the decision layer that determines where a support request goes after the AI agent has processed it. It answers three questions:

1. **Should this be routed to a human?** (escalation decision)
2. **Which tier should handle it?** (L1, L2, or L3)
3. **How urgently?** (priority + SLA deadline)

Routing is deterministic — given the same triage metadata, the same routing decision is always made. This makes it auditable and predictable.

---

## 1.2 Routing Inputs

Every routing decision is based on a **triage payload** produced by the AI agent:

```json
{
  "intent": "integration_question",
  "audience": "developer",
  "priority": "high",
  "summary": "SDK throws 401 on payment.send() despite valid API key",
  "suggested_tier": "L2",
  "escalation_reason": "Requires debugging SDK auth headers",
  "confidence": 0.61
}
```

| Field | Source | Used for |
|---|---|---|
| `intent` | AI classification | Override rules (security → L3, billing → L1) |
| `audience` | AI classification + user metadata | Enterprise gets L1 minimum |
| `priority` | AI classification | SLA deadline calculation |
| `suggested_tier` | AI suggestion | Starting point for tier assignment |
| `confidence` | AI self-assessment | Escalation trigger threshold |

---

## 1.3 Escalation Decision

Before a tier is assigned, the routing engine asks: **should a human be involved at all?**

```
should_escalate(confidence, intent, priority)
    → (True/False, reason)
```

**Escalation is forced regardless of confidence when:**

| Condition | Reason |
|---|---|
| `intent == "security"` | Security issues always require human expert review |
| `intent == "account_billing"` | Financial and account actions require human authorization |
| `priority == "critical"` | Production-impacting issues cannot wait for AI retry |

**Escalation is triggered by low confidence when:**

```
confidence < 0.70  →  escalate with reason: "AI confidence X% below threshold 70%"
```

The 0.70 threshold is configurable via `AI_CONFIDENCE_THRESHOLD` in `.env`. Raising it escalates more aggressively; lowering it lets the AI handle more autonomously.

---

## 1.4 Tier Assignment Logic

Once escalation is decided, the routing engine assigns the specific tier using this decision tree:

```
determine_tier(triage)

1. intent == "security"?
   └── L3 (always)

2. priority == "critical"?
   └── L2 minimum (override tier0/L1 suggestions)

3. audience == "enterprise" AND suggested == "tier0"?
   └── L1 minimum (enterprise never gets AI-only)

4. Otherwise → map suggested_tier directly:
   tier0 → Tier 0 (AI handles)
   L1    → L1
   L2    → L2
   L3    → L3
```

**Tier escalation path (when manually escalating an existing ticket):**

```
Tier 0 → L1 → L2 → L3
```

Each step up resets the SLA clock with the new tier's SLA for the same priority.

---

## 1.5 SLA Configuration

SLAs are defined per tier and per priority. All times represent **hours to first human response**.

| Tier | Critical | High | Medium | Low |
|---|---|---|---|---|
| **L1** | 1h | 4h | 12h | 24h |
| **L2** | 4h | 12h | 24h | 72h |
| **L3** | 8h | 24h | 72h | 168h |

SLA deadlines are computed at ticket creation:

```python
sla_deadline = datetime.now(UTC) + timedelta(hours=sla_config[tier][priority])
```

**SLA states:**

```
created → [sla_at_risk when <20% time left] → [sla_breached when deadline passed]
```

Breaches are detected lazily on ticket list queries and written back to the database. A background job (cronable via the `/crons` endpoint) can sweep for breaches on a schedule.

---

## 1.6 Ticket Lifecycle

```
open  ──►  in_progress  ──►  resolved  ──►  closed
  │              │
  └──────────────►  escalated  ──► [new tier, new SLA]
```

| Status | Meaning | SLA timer |
|---|---|---|
| `open` | Created, not yet assigned | Running |
| `in_progress` | Assigned to an agent | Running |
| `escalated` | Moved to a higher tier | Reset |
| `resolved` | Answer delivered, pending confirmation | Stopped |
| `closed` | Confirmed resolved or timed out | Stopped |

`first_response_at` is stamped when a ticket is first assigned. `resolved_at` is stamped when status moves to `resolved`.

---

## 1.7 Routing API Reference

| Endpoint | Method | Purpose |
|---|---|---|
| `POST /chat/message` | POST | Chat + auto-route on escalation |
| `GET /tickets` | GET | List tickets with filters (status, tier, priority, audience) |
| `PATCH /tickets/{id}` | PATCH | Update status, assignment, priority, tier |
| `POST /tickets/{id}/escalate` | POST | Manually escalate to next tier |
| `GET /tickets/{id}/sla` | GET | Check SLA state (deadline, hours remaining, breached) |

---

## 1.8 Routing Example: End-to-End

**Scenario:** A developer submits: *"My payment.send() call is returning 401 even though my API key works on other endpoints."*

```
Step 1 — Triage (AI):
  intent: api_question
  audience: developer
  priority: high
  confidence: 0.55
  suggested_tier: L2

Step 2 — Escalation check:
  intent != security, != billing
  priority != critical
  BUT confidence 0.55 < threshold 0.70
  → Escalate: "AI confidence 55% below threshold 70%"

Step 3 — Tier assignment:
  Not security, not critical, not enterprise
  suggested_tier = L2 → assign L2

Step 4 — SLA:
  Tier=L2, Priority=high → deadline = now + 12h

Step 5 — Ticket created:
  id: xxxxxxxx
  status: open
  tier: L2
  sla_deadline: 2026-05-13T10:00:00Z
  assigned_to: null (pending L2 agent pickup)
```

---

# Part 2: AI Agent

## 2.1 Role and Boundaries

The AI agent is the Tier 0 layer — the always-available first responder. It is powered by **Claude Opus 4.6** from Anthropic with **adaptive thinking** enabled, meaning it can reason deeply when a question warrants it.

**The agent's job:**
- Answer questions correctly using retrieved documentation
- Ask clarifying questions when the query is ambiguous
- Be honest when it doesn't know something
- Produce a confidence score and intent classification alongside every answer

**What it will not do:**
- Make promises about product timelines or undocumented features
- Access live blockchain state or user account data
- Handle security disclosures (redirects immediately)
- Execute any actions (read-only, advisory only)

---

## 2.2 Architecture

```
User message
     │
     ▼
[1] RAG Retrieval
     ├── embed query (sentence-transformers)
     ├── search ChromaDB (cosine similarity, top-5)
     └── filter: score < 0.3 dropped
     │
     ▼  context chunks (if any)
[2] Prompt Assembly
     ├── system prompt (OMS persona + instructions)
     ├── audience note (developer / enterprise / end_user)
     ├── <documentation> block (retrieved chunks)
     ├── conversation history (last 10 turns)
     └── user message
     │
     ▼
[3] Claude Opus 4.6 (streaming, adaptive thinking)
     │
     ▼
[4] Response parsing
     ├── strip <confidence> JSON block
     ├── extract score, needs_human, reason
     └── deliver display text to user
     │
     ▼
[5] Escalation check → Ticket Routing
```

---

## 2.3 System Prompt Design

The agent operates under a carefully crafted system prompt that defines its persona, scope, and output format.

**Core directives:**
1. Answer from documentation context when available — cite the source
2. Tailor tone to audience (developer = technical, enterprise = business-focused, end_user = simple)
3. Provide code examples for integration questions
4. When uncertain, be explicit: "I don't have enough information — let me connect you with our support team"
5. Always output a `<confidence>` JSON block at the end of every response

**Confidence block format:**
```json
<confidence>{"score": 0.85, "needs_human": false, "reason": null}</confidence>
```

The confidence block is stripped from the user-facing response — it's internal metadata only.

**Audience injection:**

The system prompt is augmented dynamically per request based on detected audience:

```
developer  → "The user is a developer integrating OMS."
enterprise → "The user is an enterprise partner. Be professional and thorough."
end_user   → "The user is an end user. Use simple language."
```

---

## 2.4 RAG Context Window

The agent receives up to **5 document chunks** from the knowledge base, filtered to a minimum similarity score of 0.30 (cosine). Chunks below this threshold are discarded — injecting irrelevant context is worse than injecting none.

The retrieved context is wrapped in `<documentation>` tags:

```
<documentation>
[Source: Getting Started Guide]
OMS supports Polygon PoS, Polygon zkEVM, and their testnets...

---

[Source: API Reference]
Authentication: All requests require an x-api-key header...
</documentation>

User question: Why am I getting 401 on payment.send()?
```

If no relevant context is found, the agent answers from its training knowledge and signals lower confidence accordingly.

---

## 2.5 Conversation History

The agent maintains full conversation context across turns within a session. The last **10 messages** (5 user + 5 assistant pairs) are injected into each request. This allows the agent to:

- Reference earlier parts of the conversation ("as I mentioned above...")
- Avoid repeating itself
- Understand follow-up questions in context

History beyond 10 turns is truncated from the beginning (oldest messages dropped first).

---

## 2.6 Adaptive Thinking

Claude Opus 4.6's adaptive thinking is enabled for all agent requests. This means Claude decides internally whether to reason step-by-step before answering — it does so automatically for complex questions (e.g., multi-step debugging, ambiguous errors) and skips it for simple lookups.

This delivers:
- Better accuracy on technical debugging questions
- Faster responses on simple FAQ-style queries
- No fixed token budget that could cut reasoning short

---

## 2.7 Streaming

All agent responses are streamed via **Server-Sent Events (SSE)**. The frontend receives incremental text deltas:

```
data: {"type": "text", "text": "The 401 error on "}
data: {"type": "text", "text": "payment.send() typically indicates..."}
...
data: {"type": "done", "conversation_id": "...", "ticket_id": null, "escalated": false}
```

The `done` event carries the escalation decision and ticket ID (if one was created). This allows the UI to immediately show the "ticket created" notice without a separate polling call.

---

## 2.8 Confidence Calibration

The agent's confidence score is a self-reported float from 0.0 to 1.0. It reflects the agent's own assessment of how well it answered the question given available context.

| Score range | Interpretation | Action |
|---|---|---|
| 0.85 – 1.0 | High confidence, well-sourced answer | Tier 0 resolves, no ticket |
| 0.70 – 0.84 | Moderate confidence | Tier 0 resolves, no ticket |
| < 0.70 | Low confidence | Escalate to human tier |
| `needs_human: true` | Explicit flag (security, billing, uncertainty) | Escalate regardless of score |

The 0.70 threshold is a starting point. It should be tuned based on observed data:
- If escalation rate is too high → lower threshold
- If resolution quality is too low → raise threshold

---

## 2.9 Triage Classification

In parallel with generating a user-facing answer, a separate **triage call** classifies the original user message. This uses a second Claude call with a dedicated structured-output system prompt.

Triage output fields:

| Field | Values | Purpose |
|---|---|---|
| `intent` | bug_report, integration_question, api_question, account_billing, security, onboarding, general | Routing rules |
| `audience` | developer, enterprise, end_user, unknown | Tier override, tone |
| `priority` | critical, high, medium, low | SLA deadline |
| `suggested_tier` | tier0, L1, L2, L3 | Routing hint |
| `confidence` | 0.0 – 1.0 | Escalation trigger |
| `summary` | string (≤120 chars) | Ticket subject line |
| `escalation_reason` | string or null | Human-readable escalation context |

Triage runs with adaptive thinking enabled to improve classification accuracy on ambiguous messages.

---

## 2.10 Agent API Reference

| Endpoint | Method | Description |
|---|---|---|
| `POST /chat/message` | POST | Non-streaming: full response + escalation decision |
| `POST /chat/stream` | POST | SSE streaming: text deltas + done event |

**Request body:**
```json
{
  "message": "How do I create a smart wallet?",
  "conversation_id": "conv_abc123",
  "email": "dev@example.com",
  "audience": "developer"
}
```

**Non-streaming response:**
```json
{
  "conversation_id": "conv_abc123",
  "message_id": "msg_xyz",
  "response": "To create a smart wallet using ERC-4337...",
  "confidence": 0.88,
  "escalated": false,
  "ticket_id": null,
  "tier": null,
  "triage": { "intent": "integration_question", "priority": "medium", ... }
}
```

---

# Part 3: Knowledge Base Pipeline

## 3.1 What is the KB Pipeline?

The knowledge base is the AI agent's source of truth. Without it, the agent answers purely from training data — which is generic and may not reflect OMS-specific behavior, APIs, or configurations.

The KB pipeline is a **retrieval-augmented generation (RAG)** system with four stages:

```
Documents → Chunking → Embedding → Vector Store → Retrieval
```

Every stage is designed to be incremental: new documents can be added at any time without rebuilding the entire index.

---

## 3.2 Document Sources

| Source type | Format | Cadence | Category tag |
|---|---|---|---|
| OMS official docs (GitBook) | Markdown | On release / weekly crawl | `oms_docs` |
| API reference | Markdown / OpenAPI | On API version bump | `api_reference` |
| GitHub resolved issues | Markdown (curated) | Monthly | `github_issues` |
| FAQ document | Markdown | As updated | `faq` |
| Internal runbooks | Markdown | As authored | `runbooks` |
| Support-derived FAQs | Markdown (synthesized) | Monthly | `synthetic_faq` |

---

## 3.3 Ingestion Pipeline

### Stage 1 — Load

Three input types are supported:

**Markdown / text file:**
```python
ingest_file("docs/getting_started.md", category="oms_docs")
```

**URL (web page):**
```python
ingest_url("https://docs.polygon.technology/oms/wallets", category="oms_docs")
```
The crawler strips nav/footer/script elements, extracts body text via BeautifulSoup.

**Bulk directory:**
```python
ingest_directory("./docs", glob="**/*.md", category="oms_docs")
```

### Stage 2 — Clean

Before chunking, markdown is cleaned:
- Code blocks → `[code block]` placeholder (prevents fragmented embeddings)
- Inline code → backticks removed, text preserved
- Markdown links → link text only
- Headings, bold, italic syntax → stripped

### Stage 3 — Chunk

Text is split into overlapping word windows:

```
chunk_size = 500 words
overlap     = 50 words
```

Example: a 1,200-word document produces 3 chunks:
- Chunk 0: words 0–499
- Chunk 1: words 450–949
- Chunk 2: words 900–1199

The 50-word overlap ensures context at chunk boundaries is not lost.

Each chunk carries metadata:
```python
{
    "source": "getting_started.md",
    "title": "Getting Started",
    "category": "oms_docs",
    "tags": "sdk,quickstart",
    "chunk_index": 0,
    "total_chunks": 3
}
```

### Stage 4 — Embed

Chunks are vectorized using **sentence-transformers/all-MiniLM-L6-v2**:
- 384-dimensional dense vectors
- Normalized for cosine similarity
- Runs locally, no external API call or cost

Batch embedding is used for efficiency — all chunks from a document are embedded in a single model call.

### Stage 5 — Store

Vectors are persisted in **ChromaDB** with cosine similarity configured:

```python
collection = client.get_or_create_collection(
    name="oms_knowledge",
    metadata={"hnsw:space": "cosine"}
)
collection.add(ids=..., embeddings=..., documents=..., metadatas=...)
```

ChromaDB persists to disk at `./chroma_db/`. The collection survives server restarts.

Chunk IDs follow the format: `{source}::{chunk_index}::{uuid8}`, making it possible to delete all chunks from a given source by prefix.

---

## 3.4 Retrieval

When a user sends a message, the KB pipeline:

1. Embeds the query using the same model (all-MiniLM-L6-v2)
2. Runs approximate nearest-neighbor search via HNSW index
3. Returns the top-5 chunks by cosine similarity
4. Filters out chunks with score < 0.30

```python
results = search(query="401 error on payment.send", n_results=5)
# → [
#     {"id": "...", "text": "...", "metadata": {...}, "score": 0.82},
#     {"id": "...", "text": "...", "metadata": {...}, "score": 0.71},
#     ...
# ]
```

The score is `1 - cosine_distance`, ranging from 0 (unrelated) to 1 (identical).

**Filtering by category** is supported via ChromaDB's `where` clause:
```python
search(query, where={"category": "api_reference"})
```
This is useful for routing technical API questions to API-specific docs.

---

## 3.5 Operational Commands

**Ingest the bundled docs directory:**
```bash
cd backend
python scripts/ingest_docs.py
```

**Ingest a specific URL:**
```bash
python scripts/ingest_docs.py --url https://docs.polygon.technology/oms/api --category api_reference
```

**Ingest a directory of docs:**
```bash
python scripts/ingest_docs.py --dir /path/to/docs --category oms_docs --glob "**/*.md"
```

**Check KB size (chunks):**
```bash
curl http://localhost:8000/knowledge/stats
# → {"total_chunks": 312}
```

**Search the KB:**
```bash
curl -X POST http://localhost:8000/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "how to create a smart wallet", "n_results": 3}'
```

**Ingest a URL via dashboard:**
Use the Knowledge Base page in the admin dashboard → paste a URL → click Ingest.

---

## 3.6 Knowledge Gap Monitoring

Every time the AI agent cannot answer a query (low confidence + escalation), the routing engine records a **knowledge gap signal**. Gaps can also be explicitly submitted by users via thumbs-down feedback.

```json
POST /feedback
{
  "ticket_id": "...",
  "rating": 1,
  "knowledge_gap": "Does OMS support Solana wallets?",
  "gap_category": "unsupported_chain"
}
```

The Knowledge Base dashboard surfaces the top 10 recent gaps. The documentation team reviews these monthly and adds new content to close them.

**Feedback loop cycle:**

```
AI can't answer
      │
      ▼
Escalated to human → human resolves
      │
      ▼
Gap logged in feedback table
      │
      ▼
Monthly doc review: gaps → new KB articles
      │
      ▼
New docs ingested → AI can answer next time
```

---

## 3.7 KB Quality Guidelines

When adding new documents to the knowledge base, follow these guidelines to maximize retrieval quality:

**Do:**
- Write in clear, direct prose — avoid dense jargon without explanation
- Include code examples inline (they'll become `[code block]` placeholders but surrounding explanation is retained)
- Use descriptive headings and section titles — they help with chunking context
- Keep one topic per document section
- Include error codes and their resolutions explicitly

**Avoid:**
- Tables of raw data without surrounding explanation (tables embed poorly)
- Very short documents (< 100 words) — they produce low-value single chunks
- Duplicate content across documents — causes redundant search results
- Time-sensitive content (e.g., "as of Q1 2026") without version metadata

---

## 3.8 Scaling Considerations

The current stack (ChromaDB + all-MiniLM-L6-v2 + SQLite) is designed for:
- Up to ~50,000 document chunks
- Up to ~1,000 concurrent users
- Latency < 200ms for retrieval

**When to upgrade:**

| Scale trigger | Upgrade path |
|---|---|
| > 50K chunks | Migrate ChromaDB to Weaviate or Pinecone |
| > 1K concurrent | Move embedding to batch API (voyage-3 or cohere) |
| > 100K tickets | Migrate SQLite to PostgreSQL |
| Multi-language support | Upgrade embedding model to multilingual-e5-large |

---

## 3.9 KB Pipeline API Reference

| Endpoint | Method | Description |
|---|---|---|
| `POST /knowledge/ingest/text` | POST | Ingest raw text with source/title metadata |
| `POST /knowledge/ingest/url` | POST | Crawl and ingest a URL |
| `POST /knowledge/ingest/file` | POST | Upload a file (markdown, txt) for ingestion |
| `POST /knowledge/ingest/directory` | POST | Ingest all files in a server-side directory |
| `POST /knowledge/search` | POST | Semantic search over the KB |
| `DELETE /knowledge/document/{id}` | DELETE | Delete a chunk by ID |
| `GET /knowledge/stats` | GET | Total chunk count |
| `GET /feedback/gaps` | GET | List recent knowledge gaps from user feedback |

---

## Component Interaction Summary

```
┌─────────────────────────────────────────────────────────────┐
│                    KB Pipeline                              │
│                                                             │
│  ingest_file/url  →  chunk  →  embed  →  ChromaDB         │
│                                              │              │
│                              search(query) ←┘              │
└──────────────────────────────────┬──────────────────────────┘
                                   │ top-k chunks
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                      AI Agent                               │
│                                                             │
│  assemble_prompt(chunks + history + system)                 │
│  → Claude Opus 4.6 (adaptive thinking, streaming)          │
│  → parse confidence block                                   │
│  → triage_message() → intent / audience / priority         │
└──────────────────────────────────┬──────────────────────────┘
                                   │ triage metadata + confidence
                                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Ticket Routing                            │
│                                                             │
│  should_escalate(confidence, intent, priority)              │
│  determine_tier(triage)                                     │
│  compute_sla_deadline(tier, priority)                       │
│  → create Ticket (SQLite)                                   │
│  → assign to L1 / L2 / L3 queue                            │
└─────────────────────────────────────────────────────────────┘
```

---

*Document owner: Polygon OMS Team*
*Next review: 2026-08-01*

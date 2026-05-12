# OMS Support Model
### Open Money Stack by Polygon — Internal Reference Document
**Version 1.0 | May 2026**

---

## Executive Summary

This document describes the end-to-end customer support model for Open Money Stack (OMS) by Polygon. The model combines an AI-powered first-response layer with a structured human escalation hierarchy (L1 → L2 → L3), designed to serve three distinct audiences: **developers/builders**, **enterprise partners**, and **end users** of products built on OMS.

The primary goals are:
- Resolve 60–70% of tickets autonomously via AI (Tier 0)
- Guarantee SLA-bound human responses for escalated tickets
- Continuously improve the knowledge base from support interactions
- Provide full visibility via an analytics dashboard

---

## 1. Support Architecture

```
User Query (Web Widget / Email)
         │
         ▼
┌─────────────────────┐
│   Tier 0: AI Agent  │  ← Claude Opus 4.6, RAG over OMS docs
│   (Always-on)       │    ~60–70% resolution target
└─────────┬───────────┘
          │  Low confidence / security / billing / critical
          ▼
┌─────────────────────┐
│  L1: General Support│  SLA: 4h response
│  (Human)            │    Account, onboarding, basic questions
└─────────┬───────────┘
          │  Technical depth needed
          ▼
┌─────────────────────┐
│  L2: DevRel / SE    │  SLA: 24h response
│  (Human)            │    SDK, API, integration issues
└─────────┬───────────┘
          │  Protocol / security / confirmed bugs
          ▼
┌─────────────────────┐
│  L3: Engineering    │  SLA: 72h response
│  (Human)            │    Core protocol, security disclosures
└─────────────────────┘
```

---

## 2. Tier Definitions

### Tier 0 — AI Support Agent

| Attribute | Detail |
|---|---|
| **Ownership** | Product / AI team |
| **Staffing** | Automated (Claude Opus 4.6 + RAG) |
| **Channel** | Web widget, email auto-reply |
| **Availability** | 24/7 |
| **Resolution target** | 60–70% of all tickets |
| **Escalation trigger** | Confidence < 70%, security/billing intent, critical priority |

**What the AI handles:**
- "How do I" questions (integration, SDK, API usage)
- Frequently asked questions from OMS docs
- Basic troubleshooting with code examples
- Onboarding guidance

**What the AI does NOT handle:**
- Security vulnerability reports → L3 immediately
- Billing disputes and account suspension → L1
- Confirmed production outages → L2+
- Any query where it lacks confidence

---

### L1 — General Support (Human)

| Attribute | Detail |
|---|---|
| **Team** | Support agents (non-engineering) |
| **SLA — Critical** | 1 hour first response |
| **SLA — High** | 4 hours first response |
| **SLA — Medium** | 12 hours first response |
| **SLA — Low** | 24 hours first response |

**Handles:**
- Account setup, KYC/KYB assistance (enterprise onboarding)
- Billing questions and plan changes
- Basic integration questions AI couldn't resolve
- End-user UX issues from OMS-powered products
- Bug reproduction attempts (confirm, log, escalate if needed)

**Escalates to L2 when:**
- Technical debugging is required (logs, code review)
- SDK or API behavior is unexpected
- Developer/enterprise is blocked in production

---

### L2 — Technical Support (DevRel / Solutions Engineering)

| Attribute | Detail |
|---|---|
| **Team** | Developer Relations, Solutions Engineers |
| **SLA — Critical** | 4 hours first response |
| **SLA — High** | 12 hours first response |
| **SLA — Medium** | 24 hours first response |
| **SLA — Low** | 72 hours first response |

**Handles:**
- SDK/API integration debugging
- Smart contract interaction issues
- Enterprise onboarding edge cases
- Performance investigation
- Detailed technical RCAs

**Tools available:** Staging environment access, internal runbooks, direct Slack with L3 engineering

**Escalates to L3 when:**
- Issue is a confirmed bug requiring a code fix
- Protocol-level behavior is involved
- Security concern is identified
- Enterprise SLA is at risk of breaching

---

### L3 — Engineering / Protocol Team

| Attribute | Detail |
|---|---|
| **Team** | Core engineers, protocol team |
| **SLA — Critical** | 8 hours first response |
| **SLA — High** | 24 hours first response |
| **SLA — Medium** | 72 hours first response |
| **SLA — Low** | 168 hours (1 week) first response |

**Handles:**
- Confirmed bugs (filed as GitHub issues)
- Protocol-level failures
- Security vulnerability triage and response
- Enterprise SLA breach escalations
- Post-mortem and fix deployment

**Security disclosures:** Handled via separate private channel (`security@polygon.technology`). Never routed through public ticketing.

---

## 3. Audience-Specific Handling

### Developers / Builders

- **Entry:** Web widget or email
- **Default tier:** AI → L2 if technical
- **Tone:** Technical, code-focused, precise
- **Key needs:** Working code examples, clear error explanations, fast unblocking
- **SLA priority:** High for production-impacting issues

### Enterprise Partners

- **Entry:** Dedicated email / Slack Connect channel
- **Default tier:** L1 minimum (never AI-only for enterprise)
- **Tone:** Professional, business-focused
- **Key needs:** Contractual SLAs, named account contacts, RCAs for incidents
- **SLA priority:** Per contract; L3 engaged proactively for critical issues

### End Users

- **Entry:** Web widget embedded in OMS-powered product
- **Default tier:** AI → L1
- **Tone:** Simple, non-technical, empathetic
- **Key needs:** Clear answers, easy escalation path to human
- **SLA priority:** Standard

---

## 4. Intent Classification & Routing

The AI agent automatically classifies each inbound query. Routing is determined by the combination of intent, audience, and confidence score.

| Intent | Default Tier | Always-Human? |
|---|---|---|
| `bug_report` | L2 (if confirmed) | No |
| `integration_question` | Tier 0 → L2 | No |
| `api_question` | Tier 0 → L2 | No |
| `account_billing` | L1 | **Yes** |
| `security` | L3 | **Yes — immediately** |
| `onboarding` | Tier 0 → L1 | No |
| `general` | Tier 0 | No |

**Priority thresholds:**

| Priority | Condition |
|---|---|
| **Critical** | Production down, security vuln, data loss |
| **High** | Feature broken, enterprise blocker, no workaround |
| **Medium** | Degraded performance, workaround exists |
| **Low** | Question, docs issue, feature request |

---

## 5. SLA Policy

All SLA timers start from the moment a ticket is created (either by AI escalation or direct submission).

| Tier | Critical | High | Medium | Low |
|---|---|---|---|---|
| L1 | 1h | 4h | 12h | 24h |
| L2 | 4h | 12h | 24h | 72h |
| L3 | 8h | 24h | 72h | 168h |

**SLA breach handling:**
1. Automated alert fires when < 20% of SLA time remains
2. Ticket is automatically flagged `sla_at_risk` in the dashboard
3. On breach: notify assigned agent + their manager
4. For enterprise breaches: trigger contractual incident process

---

## 6. Knowledge Base Strategy

The AI agent's quality depends entirely on the knowledge base. We manage it in four layers:

### Layer 1 — Primary Sources (Ingest immediately)
- OMS official documentation (GitBook/docs site)
- API reference (OpenAPI spec)
- SDK README files and changelogs
- Smart contract documentation

### Layer 2 — Secondary Sources (Ingest weekly)
- Resolved GitHub issues with solutions
- Discord/Telegram Q&A threads (curated)
- Internal runbooks (approved for external use)

### Layer 3 — Synthetic FAQs (Generated monthly)
- Patterns from resolved L1/L2 tickets
- Common misunderstandings detected from AI escalations
- Reviewed and approved by the DevRel team

### Layer 4 — Gap Monitoring (Continuous)
- AI flags "no document found" cases
- User thumbs-down feedback tracks unanswered topics
- Monthly gap review with doc writers to prioritize new content

---

## 7. Feedback Loop

Every AI interaction collects implicit and explicit signals to improve the system:

| Signal | Collection method | Action |
|---|---|---|
| Thumbs up/down | In-widget button after AI response | Improves confidence calibration |
| Escalation rate | Automatic tracking | Identifies weak knowledge areas |
| CSAT score | Post-resolution email survey (1–5) | Measures human tier quality |
| Knowledge gaps | AI flags "I don't know" cases | Feeds doc backlog |
| False escalations | Human agent marks "AI could have handled" | Retraining signal |

**Monthly review cadence:**
- Review AI resolution rate (target: >60%)
- Review top 10 escalated intents
- Update knowledge base based on gaps
- Adjust confidence thresholds if needed

---

## 8. Tooling Stack

| Component | Tool |
|---|---|
| AI Agent | Claude Opus 4.6 (Anthropic API) |
| Vector store (RAG) | ChromaDB (persistent) |
| Embeddings | sentence-transformers/all-MiniLM-L6-v2 |
| Backend API | FastAPI (Python) |
| Database | SQLite (SQLAlchemy) — migrate to Postgres for scale |
| Web widget | React (TypeScript) — embeddable via `<script>` tag |
| Admin dashboard | React (TypeScript) |
| Email channel | Webhook-based email parsing (integrate with SendGrid/Postmark) |

---

## 9. Metrics & KPIs

Track the following weekly in the analytics dashboard:

| Metric | Target |
|---|---|
| AI self-serve rate | ≥ 60% |
| Resolution rate (all tickets) | ≥ 85% within SLA |
| SLA breach rate | < 5% |
| Avg first response time (L1) | < 2h |
| Avg first response time (L2) | < 8h |
| CSAT score | ≥ 4.2 / 5.0 |
| Knowledge base size (chunks) | Growing week-over-week |
| Escalation rate from Tier 0 | < 40% |

---

## 10. Rollout Phases

| Phase | Timeline | Deliverable |
|---|---|---|
| **Phase 1** | Week 1–2 | Knowledge base ingestion + RAG pipeline live |
| **Phase 2** | Week 2–3 | AI agent live on web widget (beta users) |
| **Phase 3** | Week 3–4 | Ticket routing + L1/L2/L3 assignment + SLA tracking |
| **Phase 4** | Week 4 | Feedback loop + gap monitoring live |
| **Phase 5** | Week 5 | Analytics dashboard, full launch |

---

## 11. Team Responsibilities

| Role | Responsibility |
|---|---|
| **AI/Product** | Maintain AI agent, knowledge base pipeline, confidence thresholds |
| **L1 Support** | First human response, ticket triage, basic resolution |
| **DevRel / SE (L2)** | Technical resolution, developer success, runbook authorship |
| **Engineering (L3)** | Bug fixes, protocol issues, security response |
| **Documentation** | Close knowledge gaps identified by AI, weekly KB updates |
| **Security team** | Handle all `security` intent tickets, bug bounty coordination |

---

## 12. Security Policy

- Security disclosures bypass all tiers and go directly to `security@polygon.technology`
- AI agent is configured to **never** attempt to answer security questions — it immediately acknowledges and escalates
- All ticket data is stored with encryption at rest
- PII (email addresses) is minimized — only collected when needed for follow-up
- Enterprise ticket contents are treated as confidential

---

*Document owner: Polygon OMS Team*
*Next review: 2026-08-01*

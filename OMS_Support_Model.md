# OMS Support Model
### Open Money Stack by Polygon — End User Support Reference
**Version 2.0 | May 2026**

---

> **Product & Monitoring queries:** Tag `@firstresponders` on Slack.

---

## 1. Sub-Units & Escalation Matrix

| Support Unit | Scope | L1 | L2 |
|---|---|---|---|
| **OMS Portal & Transactions** | Portal queries, transaction issues (transfers, gas fees, unsupported wallets, exchanges, smart contracts), token upgrades | Mayank Singhal / Obinna Johnson | Parvez Shaikh |
| **AggLayer User Support** | Transaction-related queries on the AggLayer Portal; Datadog & Slack alert monitoring | Mayank Singhal / Obinna Johnson | Parvez Shaikh |
| **zkEVM User Support / Monitoring** | zkEVM bridge/portal queries; third-party platform issues; testnet activity; mistaken transfers (zkEVM vs PoS); unsupported wallets; alert monitoring on Slack & Datadog | Mayank Singhal | Parvez Shaikh |
| **Validator / Node Support & Monitoring** | Pre-node setup queries; node setup assistance; network monitoring with hourly Slack updates; external tx & gas fee activity from partners (Polymarket, Alchemy); comms with validators/RPC providers | Obinna Johnson | Parvez Shaikh |

**Tier 1 / Enterprise Escalations:** Routed via the BD team. Enterprise customers should contact their BD representative, who will raise escalations internally on their behalf to the support team.

---

## 1.1 Communication Modes

### External

| Channel | Description |
|---|---|
| **Primary — Tickets** | Freshdesk tickets via the ticket form on the end-user dashboard |
| **Priority — Chats** | Telegram / Discord / Slack channels, based on escalations and partner requests |
| **Tier 1 / Enterprise** | Escalations routed via the BD team. BD raises tickets internally on the customer's behalf to enterprise-support@polygon.technology |

### Internal

| Channel | Description |
|---|---|
| **Primary — Queries** | Email support-team@polygon.technology |
| **Priority — Chats** | Tag `@support-team` or `@firstresponders` on Slack |

---

## 1.2 Team Roster

Refer to the **Roster** document for POC availability and shift timings.

| Name | Role | Tier | Contact |
|---|---|---|---|
| Mayank Singhal | Support Agent | L1 | @support-team |
| Obinna Johnson | Support Agent | L1 | @support-team / @validator-support-team |
| Parvez Shaikh | Technical Lead | L2 | parvez.shaikh@polygon.technology |
| @firstresponders | Product & Monitoring | L3 | Slack tag |

---

## 2. Support Architecture

```
End User Query (Freshdesk ticket / Telegram / Discord / Slack)
         │
         ▼
┌──────────────────────────────┐
│  Tier 0: AI Agent (Optional) │  ← Claude + RAG over OMS docs
│  24/7, ~60–70% resolution    │    Escalates on low confidence
└──────────────┬───────────────┘
               │
               ▼
┌──────────────────────────────┐
│  L1 — Mayank / Obinna        │  First response ≤ 3 hrs
│  Triage, known issues,       │  Resolution ≤ 27 hrs
│  standard user queries       │
└──────────────┬───────────────┘
               │ Cannot resolve within 6 hrs / SLA breach
               ▼
┌──────────────────────────────┐
│  L2 — Parvez Shaikh          │  Acknowledge within 30 min of escalation
│  Technical investigation,    │
│  multi-user issues,          │
│  partner coordination,       │
│  on-chain anomalies          │
└──────────────┬───────────────┘
               │ Active incident / P0–P1 / security
               ▼
┌──────────────────────────────┐
│  L3 — @firstresponders       │  Immediate (P0/P1)
│  Product & Monitoring,       │
│  active exploits, chain       │
│  finality issues, enterprise  │
└──────────────────────────────┘
```

---

## 3. Escalation & Resolution Process

### 3.1 Escalation Tiers

| Tier | Who Handles | Scope | SLA Trigger |
|---|---|---|---|
| **L1** | Mayank Singhal / Obinna Johnson | First contact — ticket triage, known issues, standard user queries | First response ≤ 3 hrs; resolution ≤ 27 hrs |
| **L2** | Parvez Shaikh | Technical investigation, multi-user issues, partner coordination, on-chain anomalies | Escalate if L1 cannot resolve within 6 hrs of receipt, or at any SLA breach alert |
| **L3** | @firstresponders | Active exploits, chain/sequencer/bridge failures, enterprise incidents, Datadog/Sentry alerts unresolved by L2 | Any P0/P1; L2 unresolved within 1 hr of alert |

---

### 3.2 SLA Targets

| Metric | Target |
|---|---|
| First Response Time | 3 hours |
| Response Time | 6 hours |
| Resolution Time | 27 hours |
| First Contact Resolution | 60% |
| Response SLA | 90% |
| Resolution SLA | 90% |
| CSAT | 90% |
| Survey Response Rate | 10% |
| Reopen Rate | ≤ 10% |

---

### 3.3 SLA Breach Alerts

Freshdesk fires automated breach alerts when a ticket approaches or passes its deadline without action.

- **L1:** Immediately update the ticket with a status note and either resolve or escalate to L2 — do not let the ticket sit idle after an alert fires.
- **L2:** Acknowledge within **30 minutes** of receiving the escalation following a breach alert.
- **L3 / @firstresponders:** Tag in the relevant Slack channel if the breach involves a **P0 or P1** issue, or a Financial Partner / RSP.

Recurring breach patterns on the same issue type must be flagged to L2 for root-cause review.

---

### 3.4 Escalation Trigger Criteria

**Escalate to L2 when:**
- Ticket has not received a first response within 3 hours
- Ticket has not been resolved within 6 hours of L1 receipt, with no clear resolution path
- SLA breach alert fires with no resolution in sight
- Funds are at risk or unrecovered after 24 hours
- Issue affects multiple users simultaneously (potential systemic issue)
- Regulatory or legal risk is implicated (e.g., OFAC wallet hits, user identity disputes)
- Validator or node anomaly affecting chain health

**Escalate to L3 / @firstresponders when:**
- An active exploit or security incident is detected or suspected
- Chain finality, sequencer, or bridge contract is unresponsive
- Alert fires on Datadog / Sentry with no L2 resolution within 1 hour
- Incident affects a Financial Partner, RSP, or enterprise customer

---

### 3.5 Severity Classification

| Severity | Definition | Example | First Response | Resolution Target |
|---|---|---|---|---|
| **Critical** | Service down, funds at risk, active exploit | Bridge unresponsive; active exploit | Immediate | Immediate / 24×7 |
| **High** | Major feature broken for multiple users; partner-impacting | Staking portal errors; validator rewards failure | Immediate | Immediate / 24×7 |
| **Medium** | Single user impacted; workaround exists | Failed token upgrade; testnet faucet down | < 1 hour | < 6 hours |
| **Low** | General query; documentation gap; cosmetic bug | Delegation how-to; UI label errors | < 3 hours | < 27 hours |

---

### 3.6 Ticket Resolution Workflow

```
New Ticket Created (Freshdesk)
        ↓
L1 Triage & First Response  (TARGET: ≤ 3 hrs)
        ↓
Known Issue?
  → YES  Apply fix / KB article → Resolve → Send CSAT survey
          Update ticket: [Product | Category | Status: Resolved | Slack Link]
  → NO   ↓
Investigation & Troubleshooting
        ↓
Resolved at L1 within 27 hrs?
  → YES  Close ticket, log resolution notes
          Update ticket: [Product | Category | Status: Resolved | Slack Link]
  → NO — OR — SLA Breach Alert fires
          ↓
Escalate to L2
  → Update ticket: [Product | Category | Status: Pending | Slack Link]
  → Tag L2 in relevant Slack channel
  → L2 acknowledges within 30 mins
          ↓
Resolved at L2?
  → YES  Close ticket, notify L1 for KB capture
          Update ticket: [Product | Category | Status: Resolved | Slack Link]
  → NO  (active incident / P0–P1)
          ↓
Escalate to L3 / @firstresponders
  → Page via Zenduty (partner_critical) or Slack @firstresponders
  → Incident lead assigned
          ↓
Incident Resolved → Postmortem (P0/P1) → KB Update → Ticket Closed
```

**Ticket update format:** `[Product | Category | Status: <Resolved/Pending/Escalated> | Slack Link in Notes]`

---

### 3.7 Post-Resolution

| Item | Detail |
|---|---|
| **CSAT Survey** | Sent automatically on ticket close. Target: ≥ 90% satisfaction; ≥ 10% response rate |
| **Knowledge Base** | L1 agents document recurring issues. L2/L3 flag new issue types for KB entries after each escalation |
| **Reopen Policy** | If the same issue resurfaces within 72 hours of closure, reopen the original ticket rather than creating a new one. Target reopen rate: ≤ 10% |
| **Postmortems** | Required for all P0 and P1 incidents. Filed in the internal incident log within 5 business days of resolution |
| **SLA Reporting** | Freshdesk SLA performance reviewed against targets on a weekly/monthly basis by L2 |

---

## 4. AI Agent (Tier 0) — Optional Layer

| Attribute | Detail |
|---|---|
| **Model** | Claude Opus 4.6 (Anthropic API) + RAG over OMS docs |
| **Availability** | 24/7 |
| **Resolution target** | 60–70% of all inbound tickets |
| **Escalation trigger** | Confidence < 70%, security/billing intent, Critical/High priority |

**What the AI handles:**
- How-to questions (integration, API, SDK usage)
- FAQ from OMS documentation
- Basic troubleshooting with code examples
- Onboarding guidance

**What the AI does NOT handle:**
- Security vulnerability reports → L3 immediately
- Billing disputes / account suspension → L1
- Confirmed production outages → L2+
- Any query where it lacks confidence

---

## 5. Intent Classification & Routing

| Intent | Default Tier | Always-Human? |
|---|---|---|
| `bug_report` | L1 → L2 if confirmed | No |
| `transaction_issue` | Tier 0 → L1 | No |
| `portal_query` | Tier 0 → L1 | No |
| `staking_query` | Tier 0 → L1 | No |
| `node_validator` | L1 (Obinna) → L2 | No |
| `account_billing` | L1 | **Yes** |
| `security` | L3 / @firstresponders | **Yes — immediately** |
| `monitoring_alert` | L2 → L3 if P0/P1 | **Yes** |
| `general` | Tier 0 | No |

---

## 6. Knowledge Base Strategy

| Layer | Source | Cadence |
|---|---|---|
| **Primary** | OMS docs, API reference, SDK READMEs, smart contract docs | Ingest immediately on update |
| **Secondary** | Resolved GitHub issues, Discord/Telegram Q&A (curated), approved runbooks | Weekly |
| **Synthetic FAQs** | Patterns from resolved L1/L2 tickets, common AI escalations | Monthly |
| **Gap Monitoring** | AI "no document found" flags, thumbs-down feedback | Continuous |

---

## 7. Metrics & KPIs

| Metric | Target |
|---|---|
| First Contact Resolution | ≥ 60% |
| Response SLA compliance | ≥ 90% |
| Resolution SLA compliance | ≥ 90% |
| CSAT score | ≥ 90% |
| Survey response rate | ≥ 10% |
| Reopen rate | ≤ 10% |
| AI self-serve rate (if Tier 0 active) | ≥ 60% |
| SLA breach rate | < 5% |

---

## 8. Security Policy

- Security disclosures bypass all tiers → `security@polygon.technology` directly
- AI agent is configured to **never** attempt to answer security questions — immediately acknowledges and escalates
- All ticket data stored with encryption at rest
- PII (email addresses) minimized — collected only when needed for follow-up
- Enterprise ticket contents treated as confidential

---

*Document owner: Polygon OMS Team — Parvez Shaikh*
*Next review: 2026-08-01*

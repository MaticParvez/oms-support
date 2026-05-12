"""
Triage: classify intent, audience, priority from a user message using Claude.
Returns structured metadata to guide routing decisions.
"""
import json
import anthropic

from config import settings

_client: anthropic.Anthropic | None = None


def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None:
        _client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
    return _client


TRIAGE_SYSTEM = """You are an expert support triage system for Open Money Stack (OMS) by Polygon.
OMS is a financial infrastructure stack for building payment rails, wallets, and DeFi products on Polygon.

Your job: analyze a support message and return structured JSON with the following fields:
- intent: one of [bug_report, integration_question, api_question, account_billing, security, onboarding, general]
- audience: one of [developer, enterprise, end_user, unknown]
- priority: one of [critical, high, medium, low]
- summary: one-line summary of the issue (max 120 chars)
- suggested_tier: one of [tier0, L1, L2, L3]
  - tier0: AI can likely answer (common questions, docs, how-tos)
  - L1: needs human but non-technical (account issues, onboarding, billing)
  - L2: needs technical depth (SDK bugs, API issues, integration failures)
  - L3: needs engineering/protocol team (security issues, confirmed bugs, protocol-level failures)
- escalation_reason: why this needs human (null if tier0)
- confidence: float 0.0-1.0 — how confident you are in this classification

Priority rules:
- critical: production down, security vulnerability, data loss
- high: significant feature broken, enterprise blocker
- medium: degraded performance, workaround exists
- low: question, feature request, docs issue

Respond ONLY with valid JSON, no markdown fences."""


def triage_message(message: str, context: str = "") -> dict:
    prompt = message
    if context:
        prompt = f"Context: {context}\n\nUser message: {message}"

    response = get_client().messages.create(
        model="claude-opus-4-6",
        max_tokens=512,
        thinking={"type": "adaptive"},
        system=TRIAGE_SYSTEM,
        messages=[{"role": "user", "content": prompt}],
    )

    # Extract text from response (adaptive thinking returns thinking + text blocks)
    text = ""
    for block in response.content:
        if block.type == "text":
            text = block.text
            break

    try:
        result = json.loads(text)
    except json.JSONDecodeError:
        # Fallback: safe defaults
        result = {
            "intent": "general",
            "audience": "unknown",
            "priority": "medium",
            "summary": message[:120],
            "suggested_tier": "L1",
            "escalation_reason": "Triage parse error",
            "confidence": 0.0,
        }

    return result

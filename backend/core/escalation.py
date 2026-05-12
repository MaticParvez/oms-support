"""
Escalation logic: determine routing tier, compute SLA deadlines, track breaches.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from config import settings
from models.ticket import TicketTier, TicketPriority, TicketStatus


def compute_sla_deadline(tier: str, priority: str) -> Optional[datetime]:
    sla_hours = settings.sla_config.get(tier, {}).get(priority)
    if sla_hours is None:
        return None
    return datetime.now(timezone.utc) + timedelta(hours=sla_hours)


def should_escalate(ai_confidence: float, intent: str, priority: str) -> tuple[bool, str]:
    """
    Returns (should_escalate, reason).
    Even if AI is confident, some cases always require a human.
    """
    always_escalate_intents = {"security", "account_billing"}
    always_escalate_priorities = {"critical"}

    if intent in always_escalate_intents:
        return True, f"Intent '{intent}' always requires human review"

    if priority in always_escalate_priorities:
        return True, f"Priority '{priority}' always requires human review"

    if ai_confidence < settings.ai_confidence_threshold:
        return True, f"AI confidence {ai_confidence:.0%} below threshold {settings.ai_confidence_threshold:.0%}"

    return False, ""


def determine_tier(triage: dict) -> TicketTier:
    intent = triage.get("intent", "general")
    priority = triage.get("priority", "medium")
    audience = triage.get("audience", "unknown")
    suggested = triage.get("suggested_tier", "L1")
    confidence = triage.get("confidence", 0.0)

    # Security always goes to L3
    if intent == "security":
        return TicketTier.L3

    # Critical priority: L2 minimum
    if priority == "critical":
        return TicketTier.L2 if suggested == "tier0" else TicketTier[suggested]

    # Enterprise gets white-glove: L1 minimum
    if audience == "enterprise" and suggested == "tier0":
        return TicketTier.L1

    # Map suggestion to tier
    tier_map = {
        "tier0": TicketTier.tier0,
        "L1": TicketTier.L1,
        "L2": TicketTier.L2,
        "L3": TicketTier.L3,
    }
    return tier_map.get(suggested, TicketTier.L1)


def next_tier(current: TicketTier) -> TicketTier:
    order = [TicketTier.tier0, TicketTier.L1, TicketTier.L2, TicketTier.L3]
    idx = order.index(current)
    return order[min(idx + 1, len(order) - 1)]


def check_sla_breach(sla_deadline: Optional[datetime]) -> bool:
    if sla_deadline is None:
        return False
    return datetime.now(timezone.utc) > sla_deadline

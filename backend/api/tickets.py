"""
Ticket management API: CRUD, escalation, assignment, SLA checks.
"""
from datetime import datetime, timezone
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.ticket import Ticket, TicketStatus, TicketTier
from core.escalation import compute_sla_deadline, next_tier, check_sla_breach

router = APIRouter(prefix="/tickets", tags=["tickets"])


class TicketUpdate(BaseModel):
    status: Optional[str] = None
    assigned_to: Optional[str] = None
    priority: Optional[str] = None
    tier: Optional[str] = None
    escalation_reason: Optional[str] = None


@router.get("")
def list_tickets(
    status: Optional[str] = Query(None),
    tier: Optional[str] = Query(None),
    audience: Optional[str] = Query(None),
    priority: Optional[str] = Query(None),
    limit: int = Query(50, le=200),
    offset: int = Query(0),
    db: Session = Depends(get_db),
):
    q = db.query(Ticket)
    if status:
        q = q.filter(Ticket.status == status)
    if tier:
        q = q.filter(Ticket.tier == tier)
    if audience:
        q = q.filter(Ticket.audience == audience)
    if priority:
        q = q.filter(Ticket.priority == priority)

    total = q.count()
    tickets = q.order_by(Ticket.created_at.desc()).offset(offset).limit(limit).all()

    # Check SLA breaches in real-time
    for t in tickets:
        if t.sla_deadline and check_sla_breach(t.sla_deadline) and not t.sla_breached:
            t.sla_breached = 1
    db.commit()

    return {"total": total, "tickets": [_serialize(t) for t in tickets]}


@router.get("/{ticket_id}")
def get_ticket(ticket_id: str, db: Session = Depends(get_db)):
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")
    return _serialize(t)


@router.patch("/{ticket_id}")
def update_ticket(ticket_id: str, update: TicketUpdate, db: Session = Depends(get_db)):
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")

    if update.status:
        t.status = update.status
        if update.status == TicketStatus.resolved:
            t.resolved_at = datetime.now(timezone.utc)
    if update.assigned_to:
        t.assigned_to = update.assigned_to
        if not t.first_response_at:
            t.first_response_at = datetime.now(timezone.utc)
    if update.priority:
        t.priority = update.priority
        t.sla_deadline = compute_sla_deadline(t.tier.value, update.priority)
    if update.tier:
        t.tier = update.tier
        t.sla_deadline = compute_sla_deadline(update.tier, t.priority.value)
    if update.escalation_reason:
        t.escalation_reason = update.escalation_reason

    t.updated_at = datetime.now(timezone.utc)
    db.commit()
    return _serialize(t)


@router.post("/{ticket_id}/escalate")
def escalate_ticket(
    ticket_id: str,
    reason: str = Query(...),
    db: Session = Depends(get_db),
):
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")

    new_tier = next_tier(t.tier)
    t.tier = new_tier
    t.status = TicketStatus.escalated
    t.escalation_reason = reason
    t.sla_deadline = compute_sla_deadline(new_tier.value, t.priority.value)
    t.updated_at = datetime.now(timezone.utc)
    db.commit()

    return {"ticket_id": ticket_id, "new_tier": new_tier.value, "sla_deadline": t.sla_deadline}


@router.get("/{ticket_id}/sla")
def check_sla(ticket_id: str, db: Session = Depends(get_db)):
    t = db.query(Ticket).filter(Ticket.id == ticket_id).first()
    if not t:
        raise HTTPException(404, "Ticket not found")

    now = datetime.now(timezone.utc)
    breached = check_sla_breach(t.sla_deadline)
    time_left = None
    if t.sla_deadline:
        delta = t.sla_deadline - now
        time_left = max(0, delta.total_seconds() / 3600)  # hours

    return {
        "ticket_id": ticket_id,
        "sla_deadline": t.sla_deadline,
        "breached": breached,
        "hours_remaining": round(time_left, 2) if time_left is not None else None,
    }


def _serialize(t: Ticket) -> dict:
    return {
        "id": t.id,
        "subject": t.subject,
        "description": t.description,
        "status": t.status.value if t.status else None,
        "priority": t.priority.value if t.priority else None,
        "tier": t.tier.value if t.tier else None,
        "audience": t.audience.value if t.audience else None,
        "intent": t.intent.value if t.intent else None,
        "email": t.email,
        "company": t.company,
        "ai_confidence": t.ai_confidence,
        "escalation_reason": t.escalation_reason,
        "assigned_to": t.assigned_to,
        "sla_deadline": t.sla_deadline.isoformat() if t.sla_deadline else None,
        "sla_breached": bool(t.sla_breached),
        "first_response_at": t.first_response_at.isoformat() if t.first_response_at else None,
        "resolved_at": t.resolved_at.isoformat() if t.resolved_at else None,
        "created_at": t.created_at.isoformat() if t.created_at else None,
        "conversation_id": t.conversation_id,
    }

"""
Analytics API: resolution rates, escalation rates, CSAT, SLA compliance, volume trends.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy import func, case
from sqlalchemy.orm import Session

from database import get_db
from models.ticket import Ticket, TicketStatus, TicketTier
from models.feedback import Feedback

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/summary")
def get_summary(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db),
):
    since = datetime.now(timezone.utc) - timedelta(days=days)

    tickets = db.query(Ticket).filter(Ticket.created_at >= since)
    total = tickets.count()

    if total == 0:
        return {"period_days": days, "total_tickets": 0}

    resolved = tickets.filter(Ticket.status == TicketStatus.resolved).count()
    escalated = tickets.filter(Ticket.status == TicketStatus.escalated).count()
    sla_breached = tickets.filter(Ticket.sla_breached == 1).count()
    ai_handled = tickets.filter(Ticket.tier == TicketTier.tier0).count()

    # Average resolution time (hours)
    resolved_tickets = (
        db.query(Ticket)
        .filter(
            Ticket.created_at >= since,
            Ticket.resolved_at.isnot(None),
        )
        .all()
    )
    avg_resolution_h = None
    if resolved_tickets:
        deltas = [
            (t.resolved_at - t.created_at.replace(tzinfo=timezone.utc)).total_seconds() / 3600
            for t in resolved_tickets
            if t.resolved_at and t.created_at
        ]
        avg_resolution_h = round(sum(deltas) / len(deltas), 2) if deltas else None

    # CSAT
    feedbacks = db.query(Feedback).filter(
        Feedback.created_at >= since,
        Feedback.csat.isnot(None),
    ).all()
    avg_csat = round(sum(f.csat for f in feedbacks) / len(feedbacks), 2) if feedbacks else None

    # AI resolution rate
    ai_resolution_rate = round(ai_handled / total * 100, 1) if total else 0

    return {
        "period_days": days,
        "total_tickets": total,
        "resolved": resolved,
        "escalated": escalated,
        "resolution_rate_pct": round(resolved / total * 100, 1),
        "escalation_rate_pct": round(escalated / total * 100, 1),
        "ai_resolution_rate_pct": ai_resolution_rate,
        "sla_breach_rate_pct": round(sla_breached / total * 100, 1),
        "avg_resolution_hours": avg_resolution_h,
        "avg_csat": avg_csat,
        "feedback_count": len(feedbacks),
    }


@router.get("/by-tier")
def breakdown_by_tier(days: int = Query(30), db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(Ticket.tier, func.count(Ticket.id).label("count"))
        .filter(Ticket.created_at >= since)
        .group_by(Ticket.tier)
        .all()
    )
    return [{"tier": r.tier.value, "count": r.count} for r in rows]


@router.get("/by-intent")
def breakdown_by_intent(days: int = Query(30), db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(Ticket.intent, func.count(Ticket.id).label("count"))
        .filter(Ticket.created_at >= since)
        .group_by(Ticket.intent)
        .all()
    )
    return [{"intent": r.intent.value, "count": r.count} for r in rows]


@router.get("/by-audience")
def breakdown_by_audience(days: int = Query(30), db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    rows = (
        db.query(Ticket.audience, func.count(Ticket.id).label("count"))
        .filter(Ticket.created_at >= since)
        .group_by(Ticket.audience)
        .all()
    )
    return [{"audience": r.audience.value, "count": r.count} for r in rows]


@router.get("/volume")
def daily_volume(days: int = Query(30), db: Session = Depends(get_db)):
    since = datetime.now(timezone.utc) - timedelta(days=days)
    tickets = db.query(Ticket).filter(Ticket.created_at >= since).all()

    # Group by date
    buckets: dict[str, int] = {}
    for t in tickets:
        day = t.created_at.strftime("%Y-%m-%d")
        buckets[day] = buckets.get(day, 0) + 1

    return [{"date": k, "count": v} for k, v in sorted(buckets.items())]

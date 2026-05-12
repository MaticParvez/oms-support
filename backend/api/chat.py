"""
Chat API: handles real-time AI conversations, creates tickets on escalation.
"""
import json
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.conversation import Conversation, Message
from models.ticket import Ticket, TicketStatus
from core.agent import stream_response, get_response
from core.triage import triage_message
from core.escalation import determine_tier, compute_sla_deadline, should_escalate

router = APIRouter(prefix="/chat", tags=["chat"])


class ChatRequest(BaseModel):
    message: str
    conversation_id: str | None = None
    email: str | None = None
    audience: str = "unknown"  # developer | enterprise | end_user | unknown


class ChatStreamRequest(ChatRequest):
    pass


@router.post("/message")
async def chat_message(req: ChatRequest, db: Session = Depends(get_db)):
    """Non-streaming chat — returns full AI response + escalation decision."""
    conversation = _get_or_create_conversation(db, req)
    history = _get_history(db, conversation.id)

    text, confidence, doc_ids = await get_response(req.message, history, req.audience)

    # Persist user message
    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=req.message,
        is_ai=False,
    )
    db.add(user_msg)

    # Strip confidence block from displayed text
    display_text = text.split("<confidence>")[0].strip() if "<confidence>" in text else text

    # Persist assistant message
    ai_msg = Message(
        conversation_id=conversation.id,
        role="assistant",
        content=display_text,
        is_ai=True,
        retrieved_doc_ids=json.dumps(doc_ids),
    )
    db.add(ai_msg)
    db.commit()

    # Triage and escalation check
    triage = triage_message(req.message, context=req.audience)
    escalate, reason = should_escalate(
        confidence.get("score", 0.5),
        triage.get("intent", "general"),
        triage.get("priority", "medium"),
    )

    ticket_id = None
    tier = None
    if escalate or confidence.get("needs_human", False):
        ticket = _create_ticket(db, req, triage, display_text, confidence, reason, conversation.id)
        ticket_id = ticket.id
        tier = ticket.tier.value

    db.commit()

    return {
        "conversation_id": conversation.id,
        "message_id": ai_msg.id,
        "response": display_text,
        "confidence": confidence.get("score"),
        "escalated": escalate or confidence.get("needs_human", False),
        "ticket_id": ticket_id,
        "tier": tier,
        "triage": triage,
    }


@router.post("/stream")
async def chat_stream(req: ChatStreamRequest, db: Session = Depends(get_db)):
    """SSE streaming chat. Client reads `data: <json>` events."""
    conversation = _get_or_create_conversation(db, req)
    history = _get_history(db, conversation.id)

    user_msg = Message(
        conversation_id=conversation.id,
        role="user",
        content=req.message,
        is_ai=False,
    )
    db.add(user_msg)
    db.commit()

    async def event_generator():
        full_text = ""
        confidence = {}
        doc_ids = []

        async for chunk in stream_response(req.message, history, req.audience):
            if chunk["type"] == "text":
                full_text += chunk["text"]
                yield f"data: {json.dumps({'type': 'text', 'text': chunk['text']})}\n\n"
            elif chunk["type"] == "done":
                confidence = chunk["confidence"]
                doc_ids = chunk["doc_ids"]

        display_text = full_text.split("<confidence>")[0].strip() if "<confidence>" in full_text else full_text

        ai_msg = Message(
            conversation_id=conversation.id,
            role="assistant",
            content=display_text,
            is_ai=True,
            retrieved_doc_ids=json.dumps(doc_ids),
        )
        db.add(ai_msg)

        triage = triage_message(req.message, context=req.audience)
        escalate, reason = should_escalate(
            confidence.get("score", 0.5),
            triage.get("intent", "general"),
            triage.get("priority", "medium"),
        )

        ticket_id = None
        if escalate or confidence.get("needs_human", False):
            ticket = _create_ticket(db, req, triage, display_text, confidence, reason, conversation.id)
            ticket_id = ticket.id

        db.commit()

        yield f"data: {json.dumps({'type': 'done', 'conversation_id': conversation.id, 'ticket_id': ticket_id, 'escalated': escalate, 'triage': triage})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# ── helpers ──────────────────────────────────────────────────────────────────

def _get_or_create_conversation(db: Session, req: ChatRequest) -> Conversation:
    if req.conversation_id:
        conv = db.query(Conversation).filter(Conversation.id == req.conversation_id).first()
        if conv:
            return conv
    conv = Conversation(email=req.email, audience=req.audience)
    db.add(conv)
    db.flush()
    return conv


def _get_history(db: Session, conversation_id: str) -> list[dict]:
    messages = (
        db.query(Message)
        .filter(Message.conversation_id == conversation_id)
        .order_by(Message.created_at)
        .all()
    )
    return [{"role": m.role, "content": m.content} for m in messages]


def _create_ticket(
    db: Session,
    req: ChatRequest,
    triage: dict,
    ai_response: str,
    confidence: dict,
    reason: str,
    conversation_id: str,
) -> Ticket:
    from models.ticket import TicketIntent, TicketAudience, TicketPriority

    tier = determine_tier(triage)
    sla = compute_sla_deadline(tier.value, triage.get("priority", "medium"))

    ticket = Ticket(
        subject=triage.get("summary", req.message[:120]),
        description=req.message,
        status=TicketStatus.open,
        priority=TicketPriority(triage.get("priority", "medium")),
        tier=tier,
        audience=TicketAudience(triage.get("audience", "unknown")),
        intent=TicketIntent(triage.get("intent", "general")),
        email=req.email,
        ai_confidence=confidence.get("score"),
        ai_response=ai_response,
        escalation_reason=reason or confidence.get("reason"),
        sla_deadline=sla,
        conversation_id=conversation_id,
    )
    db.add(ticket)
    db.flush()
    return ticket

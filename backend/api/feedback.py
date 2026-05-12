"""
Feedback API: thumbs up/down, CSAT, and knowledge gap tracking.
"""
from typing import Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models.feedback import Feedback

router = APIRouter(prefix="/feedback", tags=["feedback"])


class FeedbackCreate(BaseModel):
    ticket_id: Optional[str] = None
    message_id: Optional[str] = None
    conversation_id: Optional[str] = None
    rating: Optional[int] = None        # 1 = thumbs down, 5 = thumbs up
    csat: Optional[int] = None          # 1–5
    comment: Optional[str] = None
    knowledge_gap: Optional[str] = None  # what couldn't be answered
    gap_category: Optional[str] = None


@router.post("")
def submit_feedback(payload: FeedbackCreate, db: Session = Depends(get_db)):
    fb = Feedback(**payload.model_dump())
    db.add(fb)
    db.commit()
    db.refresh(fb)
    return {"id": fb.id, "created_at": fb.created_at}


@router.get("/gaps")
def list_knowledge_gaps(limit: int = 50, db: Session = Depends(get_db)):
    """Returns unresolved knowledge gaps for doc team to address."""
    gaps = (
        db.query(Feedback)
        .filter(Feedback.knowledge_gap.isnot(None))
        .order_by(Feedback.created_at.desc())
        .limit(limit)
        .all()
    )
    return [
        {
            "id": g.id,
            "gap": g.knowledge_gap,
            "category": g.gap_category,
            "ticket_id": g.ticket_id,
            "created_at": g.created_at,
        }
        for g in gaps
    ]

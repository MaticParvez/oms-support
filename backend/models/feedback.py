from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
import uuid

from database import Base


class Feedback(Base):
    __tablename__ = "feedbacks"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    ticket_id = Column(String, ForeignKey("tickets.id"), nullable=True)
    message_id = Column(String, ForeignKey("messages.id"), nullable=True)
    conversation_id = Column(String, nullable=True)

    rating = Column(Integer, nullable=True)    # 1=thumbs down, 5=thumbs up
    csat = Column(Integer, nullable=True)      # 1–5 CSAT score
    comment = Column(Text, nullable=True)

    # Gap tracking: if AI couldn't answer, what was the topic?
    knowledge_gap = Column(Text, nullable=True)
    gap_category = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    ticket = relationship("Ticket", back_populates="feedbacks")

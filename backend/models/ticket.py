from datetime import datetime, timezone
from sqlalchemy import Column, String, Integer, DateTime, Text, Float, Enum as SAEnum
from sqlalchemy.orm import relationship
import enum
import uuid

from database import Base


class TicketStatus(str, enum.Enum):
    open = "open"
    in_progress = "in_progress"
    escalated = "escalated"
    resolved = "resolved"
    closed = "closed"


class TicketPriority(str, enum.Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"


class TicketTier(str, enum.Enum):
    tier0 = "tier0"  # AI-handled
    L1 = "L1"
    L2 = "L2"
    L3 = "L3"


class TicketAudience(str, enum.Enum):
    developer = "developer"
    enterprise = "enterprise"
    end_user = "end_user"
    unknown = "unknown"


class TicketIntent(str, enum.Enum):
    bug_report = "bug_report"
    integration_question = "integration_question"
    api_question = "api_question"
    account_billing = "account_billing"
    security = "security"
    onboarding = "onboarding"
    general = "general"


class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject = Column(String, nullable=False)
    description = Column(Text, nullable=False)

    status = Column(SAEnum(TicketStatus), default=TicketStatus.open, nullable=False)
    priority = Column(SAEnum(TicketPriority), default=TicketPriority.medium, nullable=False)
    tier = Column(SAEnum(TicketTier), default=TicketTier.tier0, nullable=False)
    audience = Column(SAEnum(TicketAudience), default=TicketAudience.unknown, nullable=False)
    intent = Column(SAEnum(TicketIntent), default=TicketIntent.general, nullable=False)

    # Contact info
    email = Column(String, nullable=True)
    company = Column(String, nullable=True)

    # AI metadata
    ai_confidence = Column(Float, nullable=True)
    ai_response = Column(Text, nullable=True)
    escalation_reason = Column(String, nullable=True)

    # SLA tracking
    sla_deadline = Column(DateTime, nullable=True)
    first_response_at = Column(DateTime, nullable=True)
    resolved_at = Column(DateTime, nullable=True)
    sla_breached = Column(Integer, default=0)  # 0=no, 1=yes

    # Assignment
    assigned_to = Column(String, nullable=True)
    conversation_id = Column(String, nullable=True)

    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc),
                        onupdate=lambda: datetime.now(timezone.utc))

    feedbacks = relationship("Feedback", back_populates="ticket", cascade="all, delete-orphan")

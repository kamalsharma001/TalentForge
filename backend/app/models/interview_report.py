"""
INTERVIEW_REPORTS table.
One report per interview, written by the interviewer, optionally enriched
by AI-generated feedback, and finalised with a hire/hold/no_hire decision.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class ReportDecision(str, enum.Enum):
    hire    = "hire"
    hold    = "hold"
    no_hire = "no_hire"


class InterviewReport(Base):
    __tablename__ = "interview_reports"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── Interviewer-written content ───────────────────────────────────────
    summary          = Column(Text)           # overall narrative
    strengths        = Column(Text)
    weaknesses       = Column(Text)
    recommendation   = Column(Text)
    private_notes    = Column(Text)           # not shown to candidate

    # ── AI-generated content ──────────────────────────────────────────────
    ai_summary       = Column(Text)
    ai_strengths     = Column(Text)
    ai_weaknesses    = Column(Text)
    ai_generated_at  = Column(DateTime(timezone=True))

    # ── Decision ──────────────────────────────────────────────────────────
    decision = Column(
        SAEnum(ReportDecision, name="report_decision", create_type=True),
        nullable=True,
    )
    overall_score    = Column(Numeric(4, 2))  # computed aggregate

    # ── Visibility ────────────────────────────────────────────────────────
    is_published     = Column(Boolean, default=False, nullable=False)
    published_at     = Column(DateTime(timezone=True))

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    interview = relationship("Interview", back_populates="report")

    def __repr__(self) -> str:
        return f"<InterviewReport interview={self.interview_id} decision={self.decision}>"

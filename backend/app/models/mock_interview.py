"""
MOCK_INTERVIEWS table — candidate-initiated solo practice sessions
with AI-evaluated feedback.

Status lifecycle:
  pending → in_progress → completed
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class MockInterviewStatus(str, enum.Enum):
    pending     = "pending"
    in_progress = "in_progress"
    completed   = "completed"


class MockInterview(Base):
    __tablename__ = "mock_interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Relationships ─────────────────────────────────────────────────────
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    practice_question_id = Column(
        UUID(as_uuid=True),
        ForeignKey("practice_questions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Session details ───────────────────────────────────────────────────
    job_role       = Column(String(150))
    difficulty     = Column(String(20))          # easy / medium / hard
    category       = Column(String(30))          # behavioral / technical / system_design
    question_text  = Column(Text, nullable=False)
    answer_text    = Column(Text)
    duration_mins  = Column(Integer, default=30)

    # ── Status ────────────────────────────────────────────────────────────
    status = Column(
        SAEnum(MockInterviewStatus, name="mock_interview_status", create_type=True),
        nullable=False,
        default=MockInterviewStatus.pending,
        index=True,
    )

    # ── AI feedback ───────────────────────────────────────────────────────
    ai_summary      = Column(Text)
    ai_strengths    = Column(Text)
    ai_weaknesses   = Column(Text)
    ai_score        = Column(Integer)
    ai_generated_at = Column(DateTime(timezone=True))

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
    completed_at = Column(DateTime(timezone=True))

    # ── Relationships ─────────────────────────────────────────────────────
    candidate         = relationship("Candidate",        backref="mock_interviews")
    practice_question = relationship("PracticeQuestion", backref="mock_interviews")

    def __repr__(self) -> str:
        return f"<MockInterview {self.id} [{self.status}]>"

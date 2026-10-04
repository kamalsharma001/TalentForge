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

    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    resume_id = Column(
        UUID(as_uuid=True),
        ForeignKey("resumes.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Session details ───────────────────────────────────────────────────
    job_role       = Column(String(150))
    difficulty     = Column(String(20))          # easy / medium / hard
    category       = Column(String(30))          # behavioral / technical / system_design
    tech_stack     = Column(ARRAY(String))       # list of skills / technologies
    question_text  = Column(Text, nullable=False)
    answer_text    = Column(Text)
    duration_mins  = Column(Integer, default=30)
    duration_mode  = Column(String(20), default="30")  # "15", "30", "45", "60", "open_ended"
    resume_snapshot = Column(Text)               # Immutable JSON snapshot of structured resume analysis
    blueprint      = Column(Text)               # Immutable JSON interview blueprint
    live_competency_state = Column(Text)        # Live competency tracking state
    live_claims_state     = Column(Text)        # Live claims tracking state

    # ── Timing & Completion ───────────────────────────────────────────────
    started_at           = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    actual_duration_secs = Column(Integer)
    completion_reason    = Column(String(50))   # "natural", "time_limit_reached", "candidate_ended"

    # ── Status ────────────────────────────────────────────────────────────
    status = Column(
        SAEnum(MockInterviewStatus, name="mock_interview_status", create_type=True),
        nullable=False,
        default=MockInterviewStatus.pending,
        index=True,
    )

    # ── AI feedback & Evaluation ──────────────────────────────────────────
    ai_summary          = Column(Text)
    ai_strengths        = Column(Text)
    ai_weaknesses       = Column(Text)
    ai_score            = Column(Integer)
    evaluation_rubric   = Column(Text)          # JSON string of multi-dimension rubric
    recommendations     = Column(Text)          # JSON string of recommended next steps
    competency_coverage = Column(Text)          # JSON string of competency coverage metrics
    validated_claims    = Column(Text)          # JSON string of validated candidate claims
    ai_generated_at     = Column(DateTime(timezone=True))

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
    interview         = relationship("Interview", foreign_keys=[interview_id])
    resume            = relationship("Resume", foreign_keys=[resume_id])
    messages          = relationship(
        "MockInterviewMessage",
        back_populates="mock_interview",
        cascade="all, delete-orphan",
        order_by="MockInterviewMessage.sequence"
    )

    def __repr__(self) -> str:
        return f"<MockInterview {self.id} [{self.status}]>"


class MockInterviewMessage(Base):
    __tablename__ = "mock_interview_messages"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    mock_interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("mock_interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    role = Column(String(20), nullable=False)      # "interviewer" or "candidate"
    content = Column(Text, nullable=False)
    sequence = Column(Integer, nullable=False)
    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    mock_interview = relationship("MockInterview", back_populates="messages")

    def __repr__(self) -> str:
        return f"<MockInterviewMessage {self.mock_interview_id} #{self.sequence} [{self.role}]>"


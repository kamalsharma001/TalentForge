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

from app import db


class MockInterviewStatus(str, enum.Enum):
    pending     = "pending"
    in_progress = "in_progress"
    completed   = "completed"


class MockInterview(db.Model):
    __tablename__ = "mock_interviews"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Relationships ─────────────────────────────────────────────────────
    candidate_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    practice_question_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("practice_questions.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Session details ───────────────────────────────────────────────────
    job_role       = db.Column(db.String(150))
    difficulty     = db.Column(db.String(20))          # easy / medium / hard
    category       = db.Column(db.String(30))          # behavioral / technical / system_design
    question_text  = db.Column(db.Text, nullable=False)
    answer_text    = db.Column(db.Text)
    duration_mins  = db.Column(db.Integer, default=30)

    # ── Status ────────────────────────────────────────────────────────────
    status = db.Column(
        SAEnum(MockInterviewStatus, name="mock_interview_status", create_type=True),
        nullable=False,
        default=MockInterviewStatus.pending,
        index=True,
    )

    # ── AI feedback ───────────────────────────────────────────────────────
    ai_summary      = db.Column(db.Text)
    ai_strengths    = db.Column(db.Text)
    ai_weaknesses   = db.Column(db.Text)
    ai_score        = db.Column(db.Integer)
    ai_generated_at = db.Column(db.DateTime(timezone=True))

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    completed_at = db.Column(db.DateTime(timezone=True))

    # ── Relationships ─────────────────────────────────────────────────────
    candidate         = db.relationship("Candidate",        backref="mock_interviews")
    practice_question = db.relationship("PracticeQuestion", backref="mock_interviews")

    def __repr__(self) -> str:
        return f"<MockInterview {self.id} [{self.status}]>"

"""
INTERVIEW_SCORES table.
Each row is one scored dimension (e.g. "Problem Solving") for an interview.
The AI feedback service aggregates these to generate summaries.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table, UniqueConstraint
from sqlalchemy.orm import relationship


class InterviewScore(Base):
    __tablename__ = "interview_scores"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interviewer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviewers.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Scoring ───────────────────────────────────────────────────────────
    dimension    = Column(String(100), nullable=False)  # "Problem Solving"
    score        = Column(Integer, nullable=False)      # 1–10
    max_score    = Column(Integer, default=10, nullable=False)
    notes        = Column(Text)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("interview_id", "dimension", name="uq_score_dimension"),
        CheckConstraint("score >= 1 AND score <= max_score", name="ck_score_range"),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    interview   = relationship("Interview",   back_populates="scores")
    interviewer = relationship("Interviewer")

    def __repr__(self) -> str:
        return f"<InterviewScore {self.dimension}={self.score}/{self.max_score}>"

"""
INTERVIEW_SCORES table.
Each row is one scored dimension (e.g. "Problem Solving") for an interview.
The AI feedback service aggregates these to generate summaries.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app import db


class InterviewScore(db.Model):
    __tablename__ = "interview_scores"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interview_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    interviewer_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("interviewers.id", ondelete="CASCADE"),
        nullable=False,
    )

    # ── Scoring ───────────────────────────────────────────────────────────
    dimension    = db.Column(db.String(100), nullable=False)  # "Problem Solving"
    score        = db.Column(db.Integer, nullable=False)      # 1–10
    max_score    = db.Column(db.Integer, default=10, nullable=False)
    notes        = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint("interview_id", "dimension", name="uq_score_dimension"),
        db.CheckConstraint("score >= 1 AND score <= max_score", name="ck_score_range"),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    interview   = db.relationship("Interview",   back_populates="scores")
    interviewer = db.relationship("Interviewer")

    def __repr__(self) -> str:
        return f"<InterviewScore {self.dimension}={self.score}/{self.max_score}>"

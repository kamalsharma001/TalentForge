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

from app import db


class ReportDecision(str, enum.Enum):
    hire    = "hire"
    hold    = "hold"
    no_hire = "no_hire"


class InterviewReport(db.Model):
    __tablename__ = "interview_reports"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interview_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("interviews.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── Interviewer-written content ───────────────────────────────────────
    summary          = db.Column(db.Text)           # overall narrative
    strengths        = db.Column(db.Text)
    weaknesses       = db.Column(db.Text)
    recommendation   = db.Column(db.Text)
    private_notes    = db.Column(db.Text)           # not shown to candidate

    # ── AI-generated content ──────────────────────────────────────────────
    ai_summary       = db.Column(db.Text)
    ai_strengths     = db.Column(db.Text)
    ai_weaknesses    = db.Column(db.Text)
    ai_generated_at  = db.Column(db.DateTime(timezone=True))

    # ── Decision ──────────────────────────────────────────────────────────
    decision = db.Column(
        SAEnum(ReportDecision, name="report_decision", create_type=True),
        nullable=True,
    )
    overall_score    = db.Column(db.Numeric(4, 2))  # computed aggregate

    # ── Visibility ────────────────────────────────────────────────────────
    is_published     = db.Column(db.Boolean, default=False, nullable=False)
    published_at     = db.Column(db.DateTime(timezone=True))

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

    # ── Relationships ─────────────────────────────────────────────────────
    interview = db.relationship("Interview", back_populates="report")

    def __repr__(self) -> str:
        return f"<InterviewReport interview={self.interview_id} decision={self.decision}>"

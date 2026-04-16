"""PRACTICE_QUESTIONS table — question bank filterable by role, difficulty, category."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app import db


class PracticeQuestion(db.Model):
    __tablename__ = "practice_questions"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Question content ──────────────────────────────────────────────────
    question      = db.Column(db.Text, nullable=False)
    job_role      = db.Column(db.String(150), nullable=False, index=True)
    difficulty    = db.Column(db.String(20),  nullable=False, index=True)   # easy / medium / hard
    category      = db.Column(db.String(30),  nullable=False, index=True)   # behavioral / technical / system_design
    hint          = db.Column(db.Text)
    sample_answer = db.Column(db.Text)
    is_active     = db.Column(db.Boolean, default=True, nullable=False)

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

    def __repr__(self) -> str:
        return f"<PracticeQuestion {self.job_role}/{self.category}/{self.difficulty}>"

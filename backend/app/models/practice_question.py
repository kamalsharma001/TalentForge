"""PRACTICE_QUESTIONS table — question bank filterable by role, difficulty, category."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class PracticeQuestion(Base):
    __tablename__ = "practice_questions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Question content ──────────────────────────────────────────────────
    question      = Column(Text, nullable=False)
    job_role      = Column(String(150), nullable=False, index=True)
    difficulty    = Column(String(20),  nullable=False, index=True)   # easy / medium / hard
    category      = Column(String(30),  nullable=False, index=True)   # behavioral / technical / system_design
    hint          = Column(Text)
    sample_answer = Column(Text)
    is_active     = Column(Boolean, default=True, nullable=False)

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

    def __repr__(self) -> str:
        return f"<PracticeQuestion {self.job_role}/{self.category}/{self.difficulty}>"

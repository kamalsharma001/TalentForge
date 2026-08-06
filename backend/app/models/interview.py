"""
INTERVIEWS table — the central entity of TalentForge.

Status lifecycle:
  pending → scheduled → completed → report_pending → (report done)
  Any status → cancelled
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class InterviewStatus(str, enum.Enum):
    pending        = "pending"
    scheduled      = "scheduled"
    completed      = "completed"
    report_pending = "report_pending"
    cancelled      = "cancelled"


class Interview(Base):
    __tablename__ = "interviews"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Relationships ─────────────────────────────────────────────────────
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    interviewer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviewers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    requested_by_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Interview details ─────────────────────────────────────────────────
    title           = Column(String(200), nullable=False)
    job_role        = Column(String(150))
    tech_stack      = Column(ARRAY(String))     # skills to assess
    difficulty      = Column(String(20))           # easy / medium / hard
    duration_mins   = Column(Integer, default=60)
    instructions    = Column(Text)                 # recruiter brief

    # ── Scheduling ────────────────────────────────────────────────────────
    scheduled_at    = Column(DateTime(timezone=True))
    timezone        = Column(String(50), default="UTC")
    meeting_link    = Column(String(500))

    # ── Status ────────────────────────────────────────────────────────────
    status = Column(
        SAEnum(InterviewStatus, name="interview_status", create_type=True),
        nullable=False,
        default=InterviewStatus.pending,
        index=True,
    )
    cancellation_reason = Column(Text)

    # ── Recording (Cloudinary) ─────────────────────────────────────────────
    recording_url        = Column(Text)
    recording_cloudinary_id = Column(String(255))
    recording_duration_s    = Column(Integer)

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
    organization  = relationship("Organization",    back_populates="interviews")
    candidate     = relationship("Candidate",       back_populates="interviews")
    interviewer   = relationship("Interviewer",     back_populates="interviews")
    requested_by  = relationship("User",            foreign_keys=[requested_by_id])
    scores        = relationship("InterviewScore",  back_populates="interview", cascade="all, delete-orphan")
    report        = relationship("InterviewReport", back_populates="interview", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Interview {self.title} [{self.status}]>"

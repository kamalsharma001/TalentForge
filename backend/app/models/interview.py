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

from app import db


class InterviewStatus(str, enum.Enum):
    pending        = "pending"
    scheduled      = "scheduled"
    completed      = "completed"
    report_pending = "report_pending"
    cancelled      = "cancelled"


class Interview(db.Model):
    __tablename__ = "interviews"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    # ── Relationships ─────────────────────────────────────────────────────
    organization_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("organizations.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    candidate_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("candidates.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )
    interviewer_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("interviewers.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    requested_by_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Interview details ─────────────────────────────────────────────────
    title           = db.Column(db.String(200), nullable=False)
    job_role        = db.Column(db.String(150))
    tech_stack      = db.Column(db.ARRAY(db.String))     # skills to assess
    difficulty      = db.Column(db.String(20))           # easy / medium / hard
    duration_mins   = db.Column(db.Integer, default=60)
    instructions    = db.Column(db.Text)                 # recruiter brief

    # ── Scheduling ────────────────────────────────────────────────────────
    scheduled_at    = db.Column(db.DateTime(timezone=True))
    timezone        = db.Column(db.String(50), default="UTC")
    meeting_link    = db.Column(db.String(500))

    # ── Status ────────────────────────────────────────────────────────────
    status = db.Column(
        SAEnum(InterviewStatus, name="interview_status", create_type=True),
        nullable=False,
        default=InterviewStatus.pending,
        index=True,
    )
    cancellation_reason = db.Column(db.Text)

    # ── Recording (Cloudinary) ─────────────────────────────────────────────
    recording_url        = db.Column(db.Text)
    recording_cloudinary_id = db.Column(db.String(255))
    recording_duration_s    = db.Column(db.Integer)

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
    organization  = db.relationship("Organization",    back_populates="interviews")
    candidate     = db.relationship("Candidate",       back_populates="interviews")
    interviewer   = db.relationship("Interviewer",     back_populates="interviews")
    requested_by  = db.relationship("User",            foreign_keys=[requested_by_id])
    scores        = db.relationship("InterviewScore",  back_populates="interview", cascade="all, delete-orphan")
    report        = db.relationship("InterviewReport", back_populates="interview", uselist=False, cascade="all, delete-orphan")

    def __repr__(self) -> str:
        return f"<Interview {self.title} [{self.status}]>"

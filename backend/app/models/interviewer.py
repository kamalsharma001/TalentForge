"""
INTERVIEWERS table — expert profile for users with role=interviewer.
Tracks domains of expertise, rate, and aggregate stats.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app import db


class Interviewer(db.Model):
    __tablename__ = "interviewers"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── Expertise ─────────────────────────────────────────────────────────
    domains          = db.Column(db.ARRAY(db.String))    # ["Backend","System Design"]
    tech_stack       = db.Column(db.ARRAY(db.String))    # ["Python","AWS","PostgreSQL"]
    years_of_exp     = db.Column(db.Integer)
    current_company  = db.Column(db.String(150))
    current_title    = db.Column(db.String(150))
    bio              = db.Column(db.Text)
    linkedin_url     = db.Column(db.String(255))

    # ── Platform stats ────────────────────────────────────────────────────
    total_interviews = db.Column(db.Integer, default=0, nullable=False)
    avg_rating       = db.Column(db.Numeric(3, 2))       # 0.00–5.00
    is_available     = db.Column(db.Boolean, default=True, nullable=False)
    is_approved      = db.Column(db.Boolean, default=False, nullable=False)  # admin approval

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
    user               = db.relationship("User",             back_populates="interviewer_profile")
    availability_slots = db.relationship("AvailabilitySlot", back_populates="interviewer", cascade="all, delete-orphan")
    interviews         = db.relationship("Interview",        back_populates="interviewer")

    def __repr__(self) -> str:
        return f"<Interviewer user={self.user_id}>"

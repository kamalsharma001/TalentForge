"""CANDIDATES table — profile data for users with role=candidate."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app import db


class Candidate(db.Model):
    __tablename__ = "candidates"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    organization_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Professional info ─────────────────────────────────────────────────
    current_title   = db.Column(db.String(150))
    years_of_exp    = db.Column(db.Integer)
    skills          = db.Column(db.ARRAY(db.String))   # e.g. ["Python","SQL"]
    linkedin_url    = db.Column(db.String(255))
    github_url      = db.Column(db.String(255))
    portfolio_url   = db.Column(db.String(255))
    notes           = db.Column(db.Text)               # recruiter private notes

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
    user         = db.relationship("User",         back_populates="candidate_profile")
    organization = db.relationship("Organization", back_populates="candidates")
    resumes      = db.relationship("Resume",       back_populates="candidate", cascade="all, delete-orphan")
    interviews   = db.relationship("Interview",    back_populates="candidate")

    def __repr__(self) -> str:
        return f"<Candidate user={self.user_id}>"

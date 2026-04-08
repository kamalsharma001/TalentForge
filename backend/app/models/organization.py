"""ORGANIZATIONS table — companies / clients who use TalentForge."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app import db


class Organization(db.Model):
    __tablename__ = "organizations"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name        = db.Column(db.String(200), nullable=False)
    slug        = db.Column(db.String(100), unique=True, nullable=False, index=True)
    logo_url    = db.Column(db.Text)
    website     = db.Column(db.String(255))
    industry    = db.Column(db.String(100))
    description = db.Column(db.Text)
    is_active   = db.Column(db.Boolean, default=True, nullable=False)

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
    members    = db.relationship("OrgMember",  back_populates="organization", cascade="all, delete-orphan")
    interviews = db.relationship("Interview",  back_populates="organization")
    candidates = db.relationship("Candidate",  back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"

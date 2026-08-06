"""CANDIDATES table — profile data for users with role=candidate."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # ── Professional info ─────────────────────────────────────────────────
    current_title   = Column(String(150))
    years_of_exp    = Column(Integer)
    skills          = Column(ARRAY(String))   # e.g. ["Python","SQL"]
    linkedin_url    = Column(String(255))
    github_url      = Column(String(255))
    portfolio_url   = Column(String(255))
    notes           = Column(Text)               # recruiter private notes

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

    # ── Relationships ─────────────────────────────────────────────────────
    user         = relationship("User",         back_populates="candidate_profile")
    organization = relationship("Organization", back_populates="candidates")
    resumes      = relationship("Resume",       back_populates="candidate", cascade="all, delete-orphan")
    interviews   = relationship("Interview",    back_populates="candidate")

    def __repr__(self) -> str:
        return f"<Candidate user={self.user_id}>"

"""
INTERVIEWERS table — expert profile for users with role=interviewer.
Tracks domains of expertise, rate, and aggregate stats.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class Interviewer(Base):
    __tablename__ = "interviewers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )

    # ── Expertise ─────────────────────────────────────────────────────────
    domains          = Column(ARRAY(String))    # ["Backend","System Design"]
    tech_stack       = Column(ARRAY(String))    # ["Python","AWS","PostgreSQL"]
    years_of_exp     = Column(Integer)
    current_company  = Column(String(150))
    current_title    = Column(String(150))
    bio              = Column(Text)
    linkedin_url     = Column(String(255))

    # ── Platform stats ────────────────────────────────────────────────────
    total_interviews = Column(Integer, default=0, nullable=False)
    avg_rating       = Column(Numeric(3, 2))       # 0.00–5.00
    is_available     = Column(Boolean, default=True, nullable=False)
    is_approved      = Column(Boolean, default=False, nullable=False)  # admin approval

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
    user               = relationship("User",             back_populates="interviewer_profile")
    availability_slots = relationship("AvailabilitySlot", back_populates="interviewer", cascade="all, delete-orphan")
    interviews         = relationship("Interview",        back_populates="interviewer")

    def __repr__(self) -> str:
        return f"<Interviewer user={self.user_id}>"

"""ORGANIZATIONS table — companies / clients who use TalentForge."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class Organization(Base):
    __tablename__ = "organizations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    name        = Column(String(200), nullable=False)
    slug        = Column(String(100), unique=True, nullable=False, index=True)
    logo_url    = Column(Text)
    website     = Column(String(255))
    industry    = Column(String(100))
    description = Column(Text)
    is_active   = Column(Boolean, default=True, nullable=False)

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
    members    = relationship("OrgMember",  back_populates="organization", cascade="all, delete-orphan")
    interviews = relationship("Interview",  back_populates="organization")
    candidates = relationship("Candidate",  back_populates="organization")

    def __repr__(self) -> str:
        return f"<Organization {self.name}>"

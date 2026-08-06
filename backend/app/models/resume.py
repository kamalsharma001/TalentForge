"""RESUMES table — Cloudinary-stored resume documents per candidate."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class Resume(Base):
    __tablename__ = "resumes"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    candidate_id = Column(
        UUID(as_uuid=True),
        ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Cloudinary metadata ───────────────────────────────────────────────
    file_name        = Column(String(255), nullable=False)
    cloudinary_url   = Column(Text, nullable=False)
    cloudinary_id    = Column(String(255), nullable=False)
    file_size_bytes  = Column(Integer)
    mime_type        = Column(String(100))

    is_primary = Column(Boolean, default=False, nullable=False)

    uploaded_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    candidate = relationship("Candidate", back_populates="resumes")

    def __repr__(self) -> str:
        return f"<Resume {self.file_name} candidate={self.candidate_id}>"

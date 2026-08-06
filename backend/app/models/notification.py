"""NOTIFICATIONS table — in-app and email notification records."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class Notification(Base):
    __tablename__ = "notifications"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Content ───────────────────────────────────────────────────────────
    title   = Column(String(255), nullable=False)
    body    = Column(Text, nullable=False)
    type    = Column(String(50))          # interview_scheduled | report_ready | …
    action_url = Column(String(500))      # deep-link in frontend

    # ── Optional link to an interview ─────────────────────────────────────
    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── State ─────────────────────────────────────────────────────────────
    is_read    = Column(Boolean, default=False, nullable=False)
    read_at    = Column(DateTime(timezone=True))
    sent_email = Column(Boolean, default=False, nullable=False)

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user = relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification [{self.type}] user={self.user_id}>"

"""
AVAILABILITY_SLOTS table.
Interviewers declare windows when they can conduct interviews.
The scheduling service matches these against requested interview times.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table
from sqlalchemy.orm import relationship


class AvailabilitySlot(Base):
    __tablename__ = "availability_slots"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interviewer_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviewers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Time window ───────────────────────────────────────────────────────
    start_time = Column(DateTime(timezone=True), nullable=False)
    end_time   = Column(DateTime(timezone=True), nullable=False)
    timezone   = Column(String(50), default="UTC", nullable=False)

    # ── State ─────────────────────────────────────────────────────────────
    is_booked  = Column(Boolean, default=False, nullable=False)
    # interview that claimed this slot (nullable until booked)
    interview_id = Column(
        UUID(as_uuid=True),
        ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Recurrence (simple support) ───────────────────────────────────────
    is_recurring      = Column(Boolean, default=False, nullable=False)
    recurrence_rule   = Column(String(100))    # e.g. "WEEKLY" | "DAILY"

    created_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        CheckConstraint("end_time > start_time", name="ck_slot_time_order"),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    interviewer = relationship("Interviewer", back_populates="availability_slots")
    interview   = relationship("Interview",   foreign_keys=[interview_id])

    def __repr__(self) -> str:
        return f"<AvailabilitySlot {self.start_time} – {self.end_time}>"

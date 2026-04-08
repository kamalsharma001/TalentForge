"""
AVAILABILITY_SLOTS table.
Interviewers declare windows when they can conduct interviews.
The scheduling service matches these against requested interview times.
"""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app import db


class AvailabilitySlot(db.Model):
    __tablename__ = "availability_slots"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    interviewer_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("interviewers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Time window ───────────────────────────────────────────────────────
    start_time = db.Column(db.DateTime(timezone=True), nullable=False)
    end_time   = db.Column(db.DateTime(timezone=True), nullable=False)
    timezone   = db.Column(db.String(50), default="UTC", nullable=False)

    # ── State ─────────────────────────────────────────────────────────────
    is_booked  = db.Column(db.Boolean, default=False, nullable=False)
    # interview that claimed this slot (nullable until booked)
    interview_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── Recurrence (simple support) ───────────────────────────────────────
    is_recurring      = db.Column(db.Boolean, default=False, nullable=False)
    recurrence_rule   = db.Column(db.String(100))    # e.g. "WEEKLY" | "DAILY"

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        db.CheckConstraint("end_time > start_time", name="ck_slot_time_order"),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    interviewer = db.relationship("Interviewer", back_populates="availability_slots")
    interview   = db.relationship("Interview",   foreign_keys=[interview_id])

    def __repr__(self) -> str:
        return f"<AvailabilitySlot {self.start_time} – {self.end_time}>"

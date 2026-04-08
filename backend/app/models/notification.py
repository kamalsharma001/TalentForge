"""NOTIFICATIONS table — in-app and email notification records."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app import db


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Content ───────────────────────────────────────────────────────────
    title   = db.Column(db.String(255), nullable=False)
    body    = db.Column(db.Text, nullable=False)
    type    = db.Column(db.String(50))          # interview_scheduled | report_ready | …
    action_url = db.Column(db.String(500))      # deep-link in frontend

    # ── Optional link to an interview ─────────────────────────────────────
    interview_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("interviews.id", ondelete="SET NULL"),
        nullable=True,
    )

    # ── State ─────────────────────────────────────────────────────────────
    is_read    = db.Column(db.Boolean, default=False, nullable=False)
    read_at    = db.Column(db.DateTime(timezone=True))
    sent_email = db.Column(db.Boolean, default=False, nullable=False)

    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user = db.relationship("User", back_populates="notifications")

    def __repr__(self) -> str:
        return f"<Notification [{self.type}] user={self.user_id}>"

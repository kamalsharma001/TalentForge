"""RESUMES table — Cloudinary-stored resume documents per candidate."""

import uuid
from datetime import datetime, timezone

from sqlalchemy.dialects.postgresql import UUID

from app import db


class Resume(db.Model):
    __tablename__ = "resumes"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    candidate_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("candidates.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    # ── Cloudinary metadata ───────────────────────────────────────────────
    file_name        = db.Column(db.String(255), nullable=False)
    cloudinary_url   = db.Column(db.Text, nullable=False)
    cloudinary_id    = db.Column(db.String(255), nullable=False)
    file_size_bytes  = db.Column(db.Integer)
    mime_type        = db.Column(db.String(100))

    is_primary = db.Column(db.Boolean, default=False, nullable=False)

    uploaded_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    candidate = db.relationship("Candidate", back_populates="resumes")

    def __repr__(self) -> str:
        return f"<Resume {self.file_name} candidate={self.candidate_id}>"

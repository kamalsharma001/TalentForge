"""
ORG_MEMBERS table.
A user can belong to multiple organisations with different roles.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app import db


class OrgRole(str, enum.Enum):
    owner  = "owner"
    admin  = "admin"
    member = "member"


class OrgMember(db.Model):
    __tablename__ = "org_members"

    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = db.Column(
        UUID(as_uuid=True),
        db.ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    org_role = db.Column(
        SAEnum(OrgRole, name="org_role", create_type=True),
        nullable=False,
        default=OrgRole.member,
    )
    is_active = db.Column(db.Boolean, default=True, nullable=False)

    joined_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "organization_id", name="uq_org_member"),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user         = db.relationship("User",         back_populates="org_memberships")
    organization = db.relationship("Organization", back_populates="members")

    def __repr__(self) -> str:
        return f"<OrgMember user={self.user_id} org={self.organization_id}>"

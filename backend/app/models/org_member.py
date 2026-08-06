"""
ORG_MEMBERS table.
A user can belong to multiple organisations with different roles.
"""

import enum
import uuid
from datetime import datetime, timezone

from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app.database import Base
from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text, ForeignKey, Numeric, Enum as SAEnum, CheckConstraint, ARRAY, Table, UniqueConstraint
from sqlalchemy.orm import relationship


class OrgRole(str, enum.Enum):
    owner  = "owner"
    admin  = "admin"
    member = "member"


class OrgMember(Base):
    __tablename__ = "org_members"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)

    user_id = Column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    organization_id = Column(
        UUID(as_uuid=True),
        ForeignKey("organizations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    org_role = Column(
        SAEnum(OrgRole, name="org_role", create_type=True),
        nullable=False,
        default=OrgRole.member,
    )
    is_active = Column(Boolean, default=True, nullable=False)

    joined_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    __table_args__ = (
        UniqueConstraint("user_id", "organization_id", name="uq_org_member"),
    )

    # ── Relationships ─────────────────────────────────────────────────────
    user         = relationship("User",         back_populates="org_memberships")
    organization = relationship("Organization", back_populates="members")

    def __repr__(self) -> str:
        return f"<OrgMember user={self.user_id} org={self.organization_id}>"

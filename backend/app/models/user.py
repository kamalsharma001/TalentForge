"""
USERS table.

Roles:
  admin       — platform super-admin
  recruiter   — org employee who requests interviews
  interviewer — expert who conducts interviews
  candidate   — person being interviewed
"""

import enum
import uuid
from datetime import datetime, timezone

import bcrypt
from sqlalchemy import Enum as SAEnum
from sqlalchemy.dialects.postgresql import UUID

from app import db


class UserRole(str, enum.Enum):
    admin       = "admin"
    recruiter   = "recruiter"
    interviewer = "interviewer"
    candidate   = "candidate"


class User(db.Model):
    __tablename__ = "users"

    # ── Primary key ───────────────────────────────────────────────────────
    id = db.Column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # ── Identity ──────────────────────────────────────────────────────────
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(
        SAEnum(UserRole, name="user_role", create_type=True),
        nullable=False,
    )

    # ── Profile ───────────────────────────────────────────────────────────
    first_name  = db.Column(db.String(100), nullable=False)
    last_name   = db.Column(db.String(100), nullable=False)
    avatar_url  = db.Column(db.Text)
    phone       = db.Column(db.String(30))
    is_active   = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)

    # ── Timestamps ────────────────────────────────────────────────────────
    created_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        nullable=False,
    )
    updated_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
        nullable=False,
    )

    # ── Relationships ─────────────────────────────────────────────────────
    org_memberships = db.relationship(
        "OrgMember", back_populates="user", cascade="all, delete-orphan"
    )
    interviewer_profile = db.relationship(
        "Interviewer", back_populates="user",
        uselist=False, cascade="all, delete-orphan",
    )
    candidate_profile = db.relationship(
        "Candidate", back_populates="user",
        uselist=False, cascade="all, delete-orphan",
    )
    notifications = db.relationship(
        "Notification", back_populates="user", cascade="all, delete-orphan"
    )

    # ── Password helpers ──────────────────────────────────────────────────
    def set_password(self, plain: str) -> None:
        self.password_hash = bcrypt.hashpw(
            plain.encode(), bcrypt.gensalt()
        ).decode()

    def check_password(self, plain: str) -> bool:
        return bcrypt.checkpw(plain.encode(), self.password_hash.encode())

    # ── Helpers ───────────────────────────────────────────────────────────
    @property
    def full_name(self) -> str:
        return f"{self.first_name} {self.last_name}"

    def __repr__(self) -> str:
        return f"<User {self.email} [{self.role}]>"

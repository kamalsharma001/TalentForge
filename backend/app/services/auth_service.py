"""
AuthService — all authentication business logic.
No Flask request context is used here; this layer is fully testable.
"""

import secrets

from flask_jwt_extended import create_access_token, create_refresh_token

from app import db
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.interviewer import Interviewer
from app.schemas.user_schema import UserSchema
from app.services.supabase_auth_service import SupabaseAuthService
from app.utils.errors import (
    ConflictError,
    AuthenticationError,
    ValidationError,
)
from app.utils.validators import validate_password_strength

_user_schema = UserSchema()


class AuthService:

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def register(data: dict) -> dict:
        """
        Create a new user account.
        Also bootstraps role-specific profile rows (Candidate / Interviewer).
        Returns JWT tokens + user payload.
        """
        email = data["email"].lower().strip()

        if User.query.filter_by(email=email).first():
            raise ConflictError(f"Email '{email}' is already registered.")

        password_error = validate_password_strength(data["password"])
        if password_error:
            raise ValidationError(password_error)

        role = UserRole(data["role"])

        user = User(
            email=email,
            role=role,
            first_name=data["first_name"],
            last_name=data["last_name"],
            phone=data.get("phone"),
        )
        user.set_password(data["password"])
        db.session.add(user)
        db.session.flush()   # get user.id without committing

        # Bootstrap role-specific profile ────────────────────────────────
        if role == UserRole.candidate:
            db.session.add(Candidate(user_id=user.id))
        elif role == UserRole.interviewer:
            db.session.add(Interviewer(user_id=user.id))

        db.session.commit()

        return AuthService._build_token_response(user)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def login(email: str, password: str) -> dict:
        """Validate credentials and return JWT tokens."""
        user = User.query.filter_by(email=email.lower().strip()).first()

        if not user or not user.check_password(password):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("This account has been deactivated.")

        return AuthService._build_token_response(user)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def oauth_google_start(supabase_access_token: str) -> dict:
        """
        First step of "Continue with Google".

        Verifies the Supabase-issued token (identity only) and looks the
        person up by their verified Google email in our existing users
        table — the same table/role system used by password login.

        * Existing account found  -> same shape as login(): tokens + user.
        * No account found        -> {"needs_registration": True, profile}
          so the frontend can collect a role (recruiter/interviewer/
          candidate) just like the normal registration form, without us
          ever guessing or hardcoding one.
        """
        claims = SupabaseAuthService.verify_access_token(supabase_access_token)
        profile = SupabaseAuthService.extract_profile(claims)

        user = User.query.filter_by(email=profile["email"].lower().strip()).first()

        if user is None:
            return {"needs_registration": True, **profile}

        if not user.is_active:
            raise AuthenticationError("This account has been deactivated.")

        return AuthService._build_token_response(user)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def oauth_google_complete(
        supabase_access_token: str,
        role: str,
        first_name: str = None,
        last_name: str = None,
        phone: str = None,
    ) -> dict:
        """
        Second step of "Continue with Google" — only reached when
        oauth_google_start reported no existing account.

        Creates the user the same way register() does (including the
        role-specific Candidate/Interviewer profile bootstrap), except
        the password is a random, unusable value since the person
        authenticates via Google, not a password.
        """
        claims = SupabaseAuthService.verify_access_token(supabase_access_token)
        profile = SupabaseAuthService.extract_profile(claims)
        email = profile["email"].lower().strip()

        if User.query.filter_by(email=email).first():
            raise ConflictError(f"Email '{email}' is already registered.")

        try:
            user_role = UserRole(role)
        except ValueError:
            raise ValidationError("Invalid role selection.")
        if user_role not in (UserRole.recruiter, UserRole.interviewer, UserRole.candidate):
            raise ValidationError("Invalid role selection.")

        user = User(
            email=email,
            role=user_role,
            first_name=(first_name or profile["first_name"] or "").strip() or "Google",
            last_name=(last_name or profile["last_name"] or "").strip() or "User",
            phone=phone,
            avatar_url=profile.get("avatar_url"),
            is_verified=True,  # Google already verified this email address
        )
        user.set_password(secrets.token_urlsafe(32))  # unusable random password
        db.session.add(user)
        db.session.flush()

        if user_role == UserRole.candidate:
            db.session.add(Candidate(user_id=user.id))
        elif user_role == UserRole.interviewer:
            db.session.add(Interviewer(user_id=user.id))

        db.session.commit()

        return AuthService._build_token_response(user)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def refresh_token(user_id: str) -> dict:
        """Issue a fresh access token from a valid refresh token."""
        user = User.query.get(user_id)
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive.")

        access_token = create_access_token(identity=str(user.id))
        return {"access_token": access_token}

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def change_password(user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise AuthenticationError("Current password is incorrect.")

        error = validate_password_strength(new_password)
        if error:
            raise ValidationError(error)

        user.set_password(new_password)
        db.session.commit()

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _build_token_response(user: User) -> dict:
        access_token  = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {
            "access_token":  access_token,
            "refresh_token": refresh_token,
            "user":          _user_schema.dump(user),
        }

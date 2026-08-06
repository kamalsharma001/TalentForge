"""
AuthService — all authentication business logic.
Fully native FastAPI and legacy SQLAlchemy ORM service.
"""

import secrets
from sqlalchemy.orm import Session
from app.utils.security import create_access_token, create_refresh_token
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.interviewer import Interviewer
from app.schemas.user_schema import UserResponse
from app.services.supabase_auth_service import SupabaseAuthService
from app.utils.errors import (
    ConflictError,
    AuthenticationError,
    ValidationError,
)
from app.utils.validators import validate_password_strength

class AuthService:

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def register(db: Session, data: dict) -> dict:
        """
        Create a new user account.
        Also bootstraps role-specific profile rows (Candidate / Interviewer).
        Returns JWT tokens + user payload.
        """
        email = data["email"].lower().strip()

        # Legacy ORM query
        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
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
        db.add(user)
        db.flush()   # get user.id without committing

        # Bootstrap role-specific profile ────────────────────────────────
        if role == UserRole.candidate:
            db.add(Candidate(user_id=user.id))
        elif role == UserRole.interviewer:
            db.add(Interviewer(user_id=user.id))

        db.commit()

        return AuthService._build_token_response(user)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def login(db: Session, email: str, password: str) -> dict:
        """Validate credentials and return JWT tokens."""
        user = db.query(User).filter(User.email == email.lower().strip()).first()

        if not user or not user.check_password(password):
            raise AuthenticationError("Invalid email or password.")

        if not user.is_active:
            raise AuthenticationError("This account has been deactivated.")

        return AuthService._build_token_response(user)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def oauth_google_start(db: Session, supabase_access_token: str) -> dict:
        """
        First step of "Continue with Google".
        """
        claims = SupabaseAuthService.verify_access_token(supabase_access_token)
        profile = SupabaseAuthService.extract_profile(claims)

        user = db.query(User).filter(User.email == profile["email"].lower().strip()).first()

        if user is None:
            return {"needs_registration": True, **profile}

        if not user.is_active:
            raise AuthenticationError("This account has been deactivated.")

        return AuthService._build_token_response(user)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def oauth_google_complete(
        db: Session,
        supabase_access_token: str,
        role: str,
        first_name: str = None,
        last_name: str = None,
        phone: str = None,
    ) -> dict:
        """
        Second step of "Continue with Google".
        """
        claims = SupabaseAuthService.verify_access_token(supabase_access_token)
        profile = SupabaseAuthService.extract_profile(claims)
        email = profile["email"].lower().strip()

        existing_user = db.query(User).filter(User.email == email).first()
        if existing_user:
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
        db.add(user)
        db.flush()

        if user_role == UserRole.candidate:
            db.add(Candidate(user_id=user.id))
        elif user_role == UserRole.interviewer:
            db.add(Interviewer(user_id=user.id))

        db.commit()

        return AuthService._build_token_response(user)

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def refresh_token(db: Session, user_id: str) -> dict:
        """Issue a fresh access token from a valid refresh token."""
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            raise AuthenticationError("User not found or inactive.")

        access_token = create_access_token(identity=str(user.id))
        return {"access_token": access_token}

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def change_password(db: Session, user: User, old_password: str, new_password: str) -> None:
        if not user.check_password(old_password):
            raise AuthenticationError("Current password is incorrect.")

        error = validate_password_strength(new_password)
        if error:
            raise ValidationError(error)

        user.set_password(new_password)
        db.commit()

    # ─────────────────────────────────────────────────────────────────────
    @staticmethod
    def _build_token_response(user: User) -> dict:
        access_token  = create_access_token(identity=str(user.id))
        refresh_token = create_refresh_token(identity=str(user.id))
        return {
            "access_token":  access_token,
            "refresh_token": refresh_token,
            "user":          UserResponse.model_validate(user).model_dict() if hasattr(UserResponse, "model_dict") else UserResponse.model_validate(user).model_dump(),
        }

"""
AuthService — all authentication business logic.
No Flask request context is used here; this layer is fully testable.
"""

from flask_jwt_extended import create_access_token, create_refresh_token

from app import db
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.interviewer import Interviewer
from app.schemas.user_schema import UserSchema
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

"""
Blueprint: /api/auth
Routes are thin controllers — all logic in AuthService.
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.auth import auth_bp
from app.auth.decorators import get_current_user
from app.schemas.user_schema import (
    UserRegistrationSchema,
    UserLoginSchema,
    UserSchema,
)
from app.services.auth_service import AuthService
from app.utils.errors import ValidationError as AppValidationError

_reg_schema    = UserRegistrationSchema()
_login_schema  = UserLoginSchema()
_user_schema   = UserSchema()


# ── POST /api/auth/register ───────────────────────────────────────────────────
@auth_bp.post("/register")
def register():
    errors = _reg_schema.validate(request.get_json(silent=True) or {})
    if errors:
        return jsonify({"errors": errors}), 422

    data = _reg_schema.load(request.get_json())
    result = AuthService.register(data)
    return jsonify(result), 201


# ── POST /api/auth/login ──────────────────────────────────────────────────────
@auth_bp.post("/login")
def login():
    errors = _login_schema.validate(request.get_json(silent=True) or {})
    if errors:
        return jsonify({"errors": errors}), 422

    data = _login_schema.load(request.get_json())
    result = AuthService.login(data["email"], data["password"])
    return jsonify(result), 200


# ── POST /api/auth/refresh ────────────────────────────────────────────────────
@auth_bp.post("/refresh")
@jwt_required(refresh=True)
def refresh():
    user_id = get_jwt_identity()
    result  = AuthService.refresh_token(user_id)
    return jsonify(result), 200


# ── GET /api/auth/me ──────────────────────────────────────────────────────────
@auth_bp.get("/me")
@jwt_required()
def me():
    user = get_current_user()
    return jsonify(_user_schema.dump(user)), 200


# ── POST /api/auth/logout ─────────────────────────────────────────────────────
@auth_bp.post("/logout")
@jwt_required()
def logout():
    # Stateless JWT — client simply discards token.
    # Extend here with a token blocklist if needed.
    return jsonify({"message": "Logged out successfully"}), 200


# ── POST /api/auth/change-password ───────────────────────────────────────────
@auth_bp.post("/change-password")
@jwt_required()
def change_password():
    body = request.get_json(silent=True) or {}
    old_password = body.get("old_password", "")
    new_password = body.get("new_password", "")

    if not old_password or not new_password:
        return jsonify({"error": "old_password and new_password are required"}), 422

    user = get_current_user()
    AuthService.change_password(user, old_password, new_password)
    return jsonify({"message": "Password changed successfully"}), 200

"""
RBAC decorators for TalentForge.

Usage:
    @jwt_required()
    @require_role("admin", "recruiter")
    def my_view():
        ...

The decorator reads the JWT identity (user id) from the token,
fetches the user from DB, and checks that their role is in the
allowed list.  A 403 is returned on mismatch.
"""

from functools import wraps

from flask import jsonify
from flask_jwt_extended import get_jwt_identity, verify_jwt_in_request

from app.models.user import User


def require_role(*roles: str):
    """
    Decorator factory.  Wrap *after* @jwt_required() or stand-alone
    (it calls verify_jwt_in_request internally for convenience).
    """
    def decorator(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            verify_jwt_in_request()
            user_id = get_jwt_identity()
            user = User.query.get(user_id)

            if user is None or not user.is_active:
                return jsonify({"error": "User not found or inactive"}), 401

            if user.role.value not in roles:
                return jsonify(
                    {
                        "error": "Forbidden",
                        "detail": f"Required role(s): {', '.join(roles)}",
                    }
                ), 403

            return fn(*args, **kwargs)
        return wrapper
    return decorator


def get_current_user() -> User:
    """
    Helper for route handlers — returns the authenticated User object.
    Must be called inside a jwt_required context.
    """
    user_id = get_jwt_identity()
    return User.query.get(user_id)

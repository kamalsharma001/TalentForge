"""
utils/errors.py
───────────────
Custom exception hierarchy + Flask global error handlers.

Every domain exception inherits from AppError so a single handler
at the app level can serialise all errors consistently.

Response envelope:
    { "error": "<message>", "code": "<machine-readable code>" }
"""

import logging
from flask import jsonify
from marshmallow import ValidationError as MarshmallowValidationError

logger = logging.getLogger(__name__)


# ── Custom exception hierarchy ────────────────────────────────────────────────

class AppError(Exception):
    """Base class for all application-level errors."""
    status_code: int = 500
    code:        str = "internal_error"

    def __init__(self, message: str = "An unexpected error occurred."):
        super().__init__(message)
        self.message = message

    def to_dict(self) -> dict:
        return {"error": self.message, "code": self.code}


class ValidationError(AppError):
    status_code = 422
    code        = "validation_error"


class AuthenticationError(AppError):
    status_code = 401
    code        = "authentication_error"


class ForbiddenError(AppError):
    status_code = 403
    code        = "forbidden"


class NotFoundError(AppError):
    status_code = 404
    code        = "not_found"


class ConflictError(AppError):
    status_code = 409
    code        = "conflict"


class ServiceUnavailableError(AppError):
    status_code = 503
    code        = "service_unavailable"


# ── Flask error handler registration ─────────────────────────────────────────

def register_error_handlers(app) -> None:

    # ── Our own exceptions ────────────────────────────────────────────────
    @app.errorhandler(AppError)
    def handle_app_error(exc: AppError):
        logger.warning("[%s] %s", exc.code, exc.message)
        return jsonify(exc.to_dict()), exc.status_code

    # ── Marshmallow validation errors (raised by schema.load) ─────────────
    @app.errorhandler(MarshmallowValidationError)
    def handle_marshmallow(exc: MarshmallowValidationError):
        return jsonify({"error": "Validation failed", "code": "validation_error", "details": exc.messages}), 422

    # ── Flask / Werkzeug HTTP errors ──────────────────────────────────────
    @app.errorhandler(400)
    def bad_request(exc):
        return jsonify({"error": "Bad request", "code": "bad_request"}), 400

    @app.errorhandler(401)
    def unauthorised(exc):
        return jsonify({"error": "Unauthorised", "code": "authentication_error"}), 401

    @app.errorhandler(403)
    def forbidden(exc):
        return jsonify({"error": "Forbidden", "code": "forbidden"}), 403

    @app.errorhandler(404)
    def not_found(exc):
        return jsonify({"error": "Resource not found", "code": "not_found"}), 404

    @app.errorhandler(405)
    def method_not_allowed(exc):
        return jsonify({"error": "Method not allowed", "code": "method_not_allowed"}), 405

    @app.errorhandler(422)
    def unprocessable(exc):
        return jsonify({"error": "Unprocessable entity", "code": "validation_error"}), 422

    @app.errorhandler(429)
    def too_many_requests(exc):
        return jsonify({"error": "Too many requests", "code": "rate_limited"}), 429

    @app.errorhandler(500)
    def internal_server_error(exc):
        logger.exception("Unhandled 500 error: %s", exc)
        return jsonify({"error": "Internal server error", "code": "internal_error"}), 500

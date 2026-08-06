"""
utils/errors.py
───────────────
Custom exception hierarchy + FastAPI global error handlers.
"""

import logging
from fastapi import Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

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

# ── FastAPI error handler registration ─────────────────────────────────────────

def register_error_handlers(app) -> None:

    @app.exception_handler(AppError)
    def handle_app_error(request: Request, exc: AppError):
        logger.warning("[%s] %s", exc.code, exc.message)
        return JSONResponse(content=exc.to_dict(), status_code=exc.status_code)

    @app.exception_handler(RequestValidationError)
    def handle_pydantic_validation(request: Request, exc: RequestValidationError):
        # Format the validation error response to match the user structure
        details = {}
        for err in exc.errors():
            loc = err.get("loc", [])
            # Usually loc is ("body", "field_name")
            field_name = loc[-1] if loc else "non_field_errors"
            details[str(field_name)] = [err.get("msg", "Invalid value")]

        return JSONResponse(
            content={
                "error": "Validation failed",
                "code": "validation_error",
                "details": details
            },
            status_code=422
        )

    @app.exception_handler(StarletteHTTPException)
    def handle_http_exception(request: Request, exc: StarletteHTTPException):
        status = exc.status_code
        code_map = {
            400: ("Bad request", "bad_request"),
            401: ("Unauthorised", "authentication_error"),
            403: ("Forbidden", "forbidden"),
            404: ("Resource not found", "not_found"),
            405: ("Method not allowed", "method_not_allowed"),
            422: ("Unprocessable entity", "validation_error"),
            429: ("Too many requests", "rate_limited"),
        }
        msg, code = code_map.get(status, (exc.detail or "An error occurred", "http_error"))
        return JSONResponse(content={"error": msg, "code": code}, status_code=status)

    @app.exception_handler(Exception)
    def handle_general_exception(request: Request, exc: Exception):
        logger.exception("Unhandled 500 error: %s", exc)
        return JSONResponse(
            content={"error": "Internal server error", "code": "internal_error"},
            status_code=500
        )

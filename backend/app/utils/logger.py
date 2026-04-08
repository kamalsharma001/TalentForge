"""
utils/logger.py
───────────────
Configures structured JSON logging for production (Render) and
readable colour logging for local development.

Call configure_logging() once in create_app() if you want custom config.
Flask's built-in logging is used otherwise (perfectly fine).
"""

import logging
import sys
import os


class _DevFormatter(logging.Formatter):
    """Human-friendly formatter for development."""
    GREY   = "\x1b[38;5;240m"
    CYAN   = "\x1b[36m"
    YELLOW = "\x1b[33m"
    RED    = "\x1b[31m"
    BOLD   = "\x1b[1m"
    RESET  = "\x1b[0m"

    LEVEL_COLOURS = {
        logging.DEBUG:    GREY,
        logging.INFO:     CYAN,
        logging.WARNING:  YELLOW,
        logging.ERROR:    RED,
        logging.CRITICAL: BOLD + RED,
    }

    def format(self, record: logging.LogRecord) -> str:
        colour = self.LEVEL_COLOURS.get(record.levelno, self.RESET)
        level  = f"{colour}{record.levelname:<8}{self.RESET}"
        return f"{level} {record.name}: {record.getMessage()}"


class _JsonFormatter(logging.Formatter):
    """Minimal JSON formatter for production log aggregators."""
    def format(self, record: logging.LogRecord) -> str:
        import json
        from datetime import datetime, timezone
        payload = {
            "ts":      datetime.now(timezone.utc).isoformat(),
            "level":   record.levelname,
            "logger":  record.name,
            "message": record.getMessage(),
        }
        if record.exc_info:
            payload["exc"] = self.formatException(record.exc_info)
        return json.dumps(payload)


def configure_logging(level: str = "INFO") -> None:
    """
    Apply structured logging to the root logger.
    Safe to call multiple times (idempotent).
    """
    env       = os.getenv("FLASK_ENV", "development").lower()
    formatter = _DevFormatter() if env == "development" else _JsonFormatter()
    log_level = getattr(logging, level.upper(), logging.INFO)

    root = logging.getLogger()
    if root.handlers:
        return  # already configured

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(formatter)
    root.addHandler(handler)
    root.setLevel(log_level)

    # Quieten noisy third-party loggers
    for noisy in ("werkzeug", "sqlalchemy.engine", "urllib3"):
        logging.getLogger(noisy).setLevel(logging.WARNING)

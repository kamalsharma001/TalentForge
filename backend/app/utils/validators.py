"""
utils/validators.py
───────────────────
Reusable validation helpers.
Return an error string on failure, None on success.
"""

import re
from typing import Optional


# ── Password ──────────────────────────────────────────────────────────────────

_SPECIAL = set(r"!@#$%^&*()_+-=[]{}|;:',.<>?/`~")

def validate_password_strength(password: str) -> Optional[str]:
    """
    Returns an error message if the password does not meet requirements,
    or None if it is acceptable.

    Rules:
      • At least 8 characters
      • At least one uppercase letter
      • At least one lowercase letter
      • At least one digit
      • At least one special character
    """
    if len(password) < 8:
        return "Password must be at least 8 characters long."
    if not re.search(r"[A-Z]", password):
        return "Password must contain at least one uppercase letter."
    if not re.search(r"[a-z]", password):
        return "Password must contain at least one lowercase letter."
    if not re.search(r"\d", password):
        return "Password must contain at least one digit."
    if not any(c in _SPECIAL for c in password):
        return "Password must contain at least one special character (!@#$%^&* …)."
    return None


# ── URL ───────────────────────────────────────────────────────────────────────

_URL_RE = re.compile(
    r"^(https?://)?"                        # optional scheme
    r"([\w-]+\.)+[\w-]+"                    # domain
    r"(/[\w\-._~:/?#\[\]@!$&'()*+,;=%]*)?$",
    re.IGNORECASE,
)

def validate_url(value: str) -> Optional[str]:
    if value and not _URL_RE.match(value):
        return f"'{value}' is not a valid URL."
    return None


# ── Phone ─────────────────────────────────────────────────────────────────────

_PHONE_RE = re.compile(r"^\+?[\d\s\-().]{7,20}$")

def validate_phone(value: str) -> Optional[str]:
    if value and not _PHONE_RE.match(value):
        return "Invalid phone number format."
    return None


# ── UUID ──────────────────────────────────────────────────────────────────────

_UUID_RE = re.compile(
    r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$",
    re.IGNORECASE,
)

def validate_uuid(value: str) -> Optional[str]:
    if value and not _UUID_RE.match(str(value)):
        return f"'{value}' is not a valid UUID."
    return None


# ── Score range ───────────────────────────────────────────────────────────────

def validate_score_range(score: int, min_score: int = 1, max_score: int = 10) -> Optional[str]:
    if not (min_score <= score <= max_score):
        return f"Score must be between {min_score} and {max_score}."
    return None


# ── Slug ──────────────────────────────────────────────────────────────────────

_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")

def validate_slug(value: str) -> Optional[str]:
    if value and not _SLUG_RE.match(value):
        return "Slug must be lowercase alphanumeric with hyphens only (e.g. 'my-org')."
    return None


# ── Timezone ──────────────────────────────────────────────────────────────────

def validate_timezone(tz_str: str) -> Optional[str]:
    try:
        import pytz
        pytz.timezone(tz_str)
        return None
    except Exception:
        return f"'{tz_str}' is not a recognised timezone."

from typing import Any
import base64
import json
import math

def paginate_query(
    query,
    page: int,
    per_page: int,
    *,
    max_per_page: int = 100,
) -> dict:
    """
    Paginate a standard SQLAlchemy Query object natively.

    Args:
        query:       Active SQLAlchemy Query object.
        page:        1-based page number.
        per_page:    Items per page.
        max_per_page: Hard ceiling on per_page.

    Returns:
        dict with keys: items, total, page, pages, per_page, has_next, has_prev.
    """
    page     = max(1, page)
    per_page = min(max(1, per_page), max_per_page)
    offset   = (page - 1) * per_page

    total = query.count()
    items = query.limit(per_page).offset(offset).all()
    
    pages = int(math.ceil(total / per_page)) if per_page else 0
    has_next = page < pages
    has_prev = page > 1

    return {
        "items":    items,
        "total":    total,
        "page":     page,
        "pages":    pages,
        "per_page": per_page,
        "has_next": has_next,
        "has_prev": has_prev,
    }

def cursor_encode(value: Any) -> str:
    """Encode a cursor value to a base64 string."""
    return base64.urlsafe_b64encode(json.dumps(value).encode()).decode()

def cursor_decode(cursor: str) -> Any:
    """Decode a base64 cursor back to its original value."""
    try:
        return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
    except Exception:
        return None

"""
utils/pagination.py
───────────────────
Consistent page-based pagination for SQLAlchemy queries.

Usage:
    from app.utils.pagination import paginate_query

    result = paginate_query(
        query    = User.query.filter_by(is_active=True),
        page     = 1,
        per_page = 20,
        schema   = UserSchema(),
    )
    # result → { items, total, page, pages, per_page, has_next, has_prev }
"""

from typing import Any

from marshmallow import Schema


def paginate_query(
    query,
    page: int,
    per_page: int,
    schema: Schema,
    *,
    max_per_page: int = 100,
) -> dict:
    """
    Paginate a SQLAlchemy query and serialise the results.

    Args:
        query:       Active SQLAlchemy BaseQuery / Select.
        page:        1-based page number.
        per_page:    Items per page (capped at max_per_page).
        schema:      A Marshmallow schema instance (single object, not many=True).
                     The function calls schema.dump() for each item.
        max_per_page: Hard ceiling on per_page to prevent huge responses.

    Returns:
        dict with keys: items, total, page, pages, per_page, has_next, has_prev.
    """
    page     = max(1, page)
    per_page = min(max(1, per_page), max_per_page)

    pagination = query.paginate(page=page, per_page=per_page, error_out=False)

    # Support both Schema() and Schema(many=True) instances
    if getattr(schema, "many", False):
        items = schema.dump(pagination.items)
    else:
        items = [schema.dump(item) for item in pagination.items]

    return {
        "items":    items,
        "total":    pagination.total,
        "page":     page,
        "pages":    pagination.pages,
        "per_page": per_page,
        "has_next": pagination.has_next,
        "has_prev": pagination.has_prev,
    }


def cursor_encode(value: Any) -> str:
    """Encode a cursor value to a base64 string."""
    import base64, json
    return base64.urlsafe_b64encode(json.dumps(value).encode()).decode()


def cursor_decode(cursor: str) -> Any:
    """Decode a base64 cursor back to its original value."""
    import base64, json
    try:
        return json.loads(base64.urlsafe_b64decode(cursor.encode()).decode())
    except Exception:
        return None

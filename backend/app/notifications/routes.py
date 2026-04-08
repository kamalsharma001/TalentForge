"""
Blueprint: /api/notifications
"""

from flask import request, jsonify

from app.notifications import notifications_bp
from app.auth.decorators import get_current_user
from app.services.notification_service import NotificationService
from flask_jwt_extended import jwt_required


# ── GET /api/notifications ────────────────────────────────────────────────────
@notifications_bp.get("/")
@jwt_required()
def list_notifications():
    current_user = get_current_user()
    page         = request.args.get("page", 1, type=int)
    per_page     = request.args.get("per_page", 20, type=int)
    unread_only  = request.args.get("unread_only", "false").lower() == "true"

    result = NotificationService.list_for_user(
        str(current_user.id),
        unread_only=unread_only,
        page=page,
        per_page=per_page,
    )
    return jsonify(result), 200


# ── GET /api/notifications/unread-count ───────────────────────────────────────
@notifications_bp.get("/unread-count")
@jwt_required()
def unread_count():
    current_user = get_current_user()
    count = NotificationService.unread_count(str(current_user.id))
    return jsonify({"unread_count": count}), 200


# ── PATCH /api/notifications/<id>/read ───────────────────────────────────────
@notifications_bp.patch("/<uuid:notification_id>/read")
@jwt_required()
def mark_read(notification_id):
    current_user = get_current_user()
    result = NotificationService.mark_read(str(notification_id), str(current_user.id))
    return jsonify(result), 200


# ── POST /api/notifications/mark-all-read ─────────────────────────────────────
@notifications_bp.post("/mark-all-read")
@jwt_required()
def mark_all_read():
    current_user = get_current_user()
    updated = NotificationService.mark_all_read(str(current_user.id))
    return jsonify({"updated": updated, "message": f"{updated} notifications marked as read"}), 200

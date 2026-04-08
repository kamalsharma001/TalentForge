"""
Blueprint: /api/interviews
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.interviews import interviews_bp
from app.auth.decorators import require_role, get_current_user
from app.services.interview_service import InterviewService
from app.services.notification_service import NotificationService
from app.schemas.interview_schema import (
    InterviewCreateSchema,
    InterviewUpdateSchema,
    InterviewAssignSchema,
    InterviewCompleteSchema,
)
from app.models.interviewer import Interviewer

_create_schema   = InterviewCreateSchema()
_update_schema   = InterviewUpdateSchema()
_assign_schema   = InterviewAssignSchema()
_complete_schema = InterviewCompleteSchema()


# ── POST /api/interviews ──────────────────────────────────────────────────────
@interviews_bp.post("/")
@require_role("admin", "recruiter")
def create_interview():
    body   = request.get_json(silent=True) or {}
    errors = _create_schema.validate(body)
    if errors:
        return jsonify({"errors": errors}), 422

    data        = _create_schema.load(body)
    current_user = get_current_user()
    result      = InterviewService.create(data, str(current_user.id))
    return jsonify(result), 201


# ── GET /api/interviews ───────────────────────────────────────────────────────
@interviews_bp.get("/")
@jwt_required()
def list_interviews():
    current_user = get_current_user()
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    status   = request.args.get("status")

    # Scope list by role
    kwargs = {"page": page, "per_page": per_page, "status": status}

    role = current_user.role.value
    if role == "recruiter":
        # recruiters see interviews from their orgs — simplified: filter by requested_by
        kwargs["organization_id"] = request.args.get("organization_id")
    elif role == "interviewer":
        iv = Interviewer.query.filter_by(user_id=current_user.id).first()
        if iv:
            kwargs["interviewer_id"] = str(iv.id)
    elif role == "candidate":
        from app.models.candidate import Candidate
        c = Candidate.query.filter_by(user_id=current_user.id).first()
        if c:
            kwargs["candidate_id"] = str(c.id)
    # admin sees everything

    result = InterviewService.list_interviews(**kwargs)
    return jsonify(result), 200


# ── GET /api/interviews/<id> ──────────────────────────────────────────────────
@interviews_bp.get("/<uuid:interview_id>")
@jwt_required()
def get_interview(interview_id):
    result = InterviewService.get_by_id(str(interview_id))
    return jsonify(result), 200


# ── PATCH /api/interviews/<id> ────────────────────────────────────────────────
@interviews_bp.patch("/<uuid:interview_id>")
@require_role("admin", "recruiter")
def update_interview(interview_id):
    body   = request.get_json(silent=True) or {}
    errors = _update_schema.validate(body)
    if errors:
        return jsonify({"errors": errors}), 422

    data         = _update_schema.load(body)
    current_user = get_current_user()
    result       = InterviewService.update(str(interview_id), data, str(current_user.id))
    return jsonify(result), 200


# ── POST /api/interviews/<id>/assign ─────────────────────────────────────────
@interviews_bp.post("/<uuid:interview_id>/assign")
@require_role("admin", "recruiter")
def assign_interviewer(interview_id):
    body   = request.get_json(silent=True) or {}
    errors = _assign_schema.validate(body)
    if errors:
        return jsonify({"errors": errors}), 422

    data   = _assign_schema.load(body)
    result = InterviewService.assign_interviewer(
        str(interview_id),
        str(data["interviewer_id"]),
        str(data["slot_id"]),
    )
    # Trigger notifications
    from app.models.interview import Interview
    interview = Interview.query.get(str(interview_id))
    if interview:
        NotificationService.interview_scheduled(interview)

    return jsonify(result), 200


# ── POST /api/interviews/<id>/complete ───────────────────────────────────────
@interviews_bp.post("/<uuid:interview_id>/complete")
@require_role("interviewer")
def complete_interview(interview_id):
    body   = request.get_json(silent=True) or {}
    errors = _complete_schema.validate(body)
    if errors:
        return jsonify({"errors": errors}), 422

    data         = _complete_schema.load(body)
    current_user = get_current_user()
    result       = InterviewService.complete(str(interview_id), data, str(current_user.id))
    return jsonify(result), 200


# ── POST /api/interviews/<id>/cancel ─────────────────────────────────────────
@interviews_bp.post("/<uuid:interview_id>/cancel")
@jwt_required()
def cancel_interview(interview_id):
    body         = request.get_json(silent=True) or {}
    reason       = body.get("reason")
    current_user = get_current_user()
    result       = InterviewService.cancel(str(interview_id), reason, str(current_user.id))
    return jsonify(result), 200

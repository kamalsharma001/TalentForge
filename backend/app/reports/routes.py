"""
Blueprint: /api/reports
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.reports import reports_bp
from app.auth.decorators import require_role, get_current_user
from app.services.report_service import ReportService
from app.services.notification_service import NotificationService
from app.services.ai_feedback_service import AiFeedbackService
from app.schemas.report_schema import ReportCreateSchema, ReportUpdateSchema
from app.models.interview import Interview

_create_schema = ReportCreateSchema()
_update_schema = ReportUpdateSchema()


# ── POST /api/reports/<interview_id> ──────────────────────────────────────────
@reports_bp.post("/<uuid:interview_id>")
@require_role("interviewer")
def create_report(interview_id):
    body   = request.get_json(silent=True) or {}
    errors = _create_schema.validate(body)
    if errors:
        return jsonify({"errors": errors}), 422

    data         = _create_schema.load(body)
    current_user = get_current_user()
    result       = ReportService.create(str(interview_id), data, str(current_user.id))
    return jsonify(result), 201


# ── GET /api/reports/<interview_id> ───────────────────────────────────────────
@reports_bp.get("/<uuid:interview_id>")
@jwt_required()
def get_report(interview_id):
    current_user = get_current_user()
    role = current_user.role.value

    # Candidates get a stripped view; only published reports
    as_candidate = (role == "candidate")
    result = ReportService.get_by_interview(str(interview_id), as_candidate=as_candidate)
    return jsonify(result), 200


# ── PATCH /api/reports/<report_id> ────────────────────────────────────────────
@reports_bp.patch("/<uuid:report_id>/edit")
@require_role("interviewer", "admin")
def update_report(report_id):
    body   = request.get_json(silent=True) or {}
    errors = _update_schema.validate(body)
    if errors:
        return jsonify({"errors": errors}), 422

    data         = _update_schema.load(body)
    current_user = get_current_user()
    result       = ReportService.update(str(report_id), data, str(current_user.id))
    return jsonify(result), 200


# ── POST /api/reports/<report_id>/publish ─────────────────────────────────────
@reports_bp.post("/<uuid:report_id>/publish")
@require_role("admin", "recruiter")
def publish_report(report_id):
    result = ReportService.publish(str(report_id))

    # Notify the candidate
    from app.models.interview_report import InterviewReport
    report   = InterviewReport.query.get(str(report_id))
    if report:
        interview = Interview.query.get(str(report.interview_id))
        if interview:
            NotificationService.report_published(interview)

    return jsonify(result), 200


# ── POST /api/reports/<interview_id>/generate-ai ──────────────────────────────
@reports_bp.post("/<uuid:interview_id>/generate-ai")
@require_role("admin", "recruiter", "interviewer")
def generate_ai_feedback(interview_id):
    """
    Trigger AI feedback generation for an interview.
    Attaches the result to the existing report (or creates fields for later).
    """
    ai_data = AiFeedbackService.generate(str(interview_id))

    # Attach to existing report if one exists
    interview = Interview.query.get(str(interview_id))
    if interview and interview.report:
        ReportService.attach_ai_summary(str(interview.report.id), ai_data)

    return jsonify({
        "message":   "AI feedback generated successfully",
        "ai_data":   ai_data,
    }), 200

"""
Blueprint: /api/feedback
Thin controller — all logic in AiFeedbackService.
"""

from flask import request, jsonify

from app.ai_feedback import ai_feedback_bp
from app.auth.decorators import require_role, get_current_user
from app.services.ai_feedback_service import AiFeedbackService
from app.services.report_service import ReportService
from app.models.interview import Interview


# ── POST /api/feedback/<interview_id>/generate ────────────────────────────────
@ai_feedback_bp.post("/<uuid:interview_id>/generate")
@require_role("admin", "recruiter", "interviewer")
def generate(interview_id):
    """
    Generate (or regenerate) AI feedback for a completed interview.
    Persists the result onto the associated InterviewReport.
    """
    ai_data   = AiFeedbackService.generate(str(interview_id))
    interview = Interview.query.get(str(interview_id))

    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    # create report automatically if it does not exist
    if not interview.report:
        report = ReportService.create(str(interview.id), {}, get_current_user().id)

    ReportService.attach_ai_summary(str(interview.report.id), ai_data)

    return jsonify({
        "message": "AI feedback generated",
        "summary":    ai_data.get("summary"),
        "strengths":  ai_data.get("strengths"),
        "weaknesses": ai_data.get("weaknesses"),
    }), 200


# ── GET /api/feedback/<interview_id>/preview ──────────────────────────────────
@ai_feedback_bp.get("/<uuid:interview_id>/preview")
@require_role("admin", "recruiter", "interviewer")
def preview(interview_id):
    """
    Return the AI-generated content already stored on the report
    without triggering a new generation.
    """
    interview = Interview.query.get(str(interview_id))
    if not interview:
        return jsonify({"error": "Interview not found"}), 404

    report = interview.report
    if not report or not report.ai_summary:
        return jsonify({"error": "No AI feedback found. Call /generate first."}), 404


    return jsonify({
    "summary": report.ai_summary,
    "strengths": report.ai_strengths,
    "weaknesses": report.ai_weaknesses
    }), 200

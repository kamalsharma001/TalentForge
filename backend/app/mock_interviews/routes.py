"""
Blueprint: /api/mock-interviews
Thin controller — all logic in MockInterviewService / AiFeedbackService.
"""

from flask import request, jsonify

from app.mock_interviews import mock_interviews_bp
from app.auth.decorators import require_role, get_current_user
from app.services.mock_interview_service import MockInterviewService
from app.services.ai_feedback_service import AiFeedbackService
from app.schemas.mock_interview_schema import (
    MockInterviewCreateSchema,
    MockInterviewSubmitSchema,
)


# ── POST /api/mock-interviews ─────────────────────────────────────────────
@mock_interviews_bp.post("/")
@require_role("candidate")
def create():
    """Start a new mock interview session."""
    data = MockInterviewCreateSchema().load(request.get_json(silent=True) or {})
    user = get_current_user()
    result = MockInterviewService.create(str(user.id), data)
    return jsonify(result), 201


# ── GET /api/mock-interviews ──────────────────────────────────────────────
@mock_interviews_bp.get("/")
@require_role("candidate")
def list_sessions():
    """List mock interview sessions for the current candidate."""
    user = get_current_user()
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    result = MockInterviewService.list_for_candidate(str(user.id), page, per_page)
    return jsonify(result), 200


# ── GET /api/mock-interviews/<id> ─────────────────────────────────────────
@mock_interviews_bp.get("/<uuid:session_id>")
@require_role("candidate")
def get_session(session_id):
    """Get a single mock interview session."""
    user = get_current_user()
    result = MockInterviewService.get(str(session_id), str(user.id))
    return jsonify(result), 200


# ── POST /api/mock-interviews/<id>/submit ─────────────────────────────────
@mock_interviews_bp.post("/<uuid:session_id>/submit")
@require_role("candidate")
def submit(session_id):
    """Submit a candidate's answer for a mock interview session."""
    data = MockInterviewSubmitSchema().load(request.get_json(silent=True) or {})
    user = get_current_user()
    result = MockInterviewService.submit_answer(
        str(session_id), str(user.id), data["answer_text"]
    )
    return jsonify(result), 200


# ── POST /api/mock-interviews/<id>/feedback ───────────────────────────────
@mock_interviews_bp.post("/<uuid:session_id>/feedback")
@require_role("candidate")
def generate_feedback(session_id):
    """Generate AI feedback for a completed mock interview session."""
    user = get_current_user()

    # Verify ownership first
    MockInterviewService.get(str(session_id), str(user.id))

    ai_data = AiFeedbackService.generate_mock_feedback(str(session_id))
    return jsonify({
        "message":    "AI feedback generated",
        "summary":    ai_data.get("summary"),
        "strengths":  ai_data.get("strengths"),
        "weaknesses": ai_data.get("weaknesses"),
        "score":      ai_data.get("score"),
    }), 200

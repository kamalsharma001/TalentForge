"""
Blueprint: /api/practice
Thin controller — all logic in PracticeService.
"""

from flask import request, jsonify

from app.practice import practice_bp
from app.auth.decorators import require_role
from app.services.practice_service import PracticeService
from app.schemas.practice_schema import PracticeQuestionCreateSchema


# ── GET /api/practice ─────────────────────────────────────────────────────
@practice_bp.get("/")
@require_role("candidate", "admin", "recruiter", "interviewer")
def list_questions():
    """List practice questions with optional filters."""
    page       = request.args.get("page", 1, type=int)
    per_page   = request.args.get("per_page", 20, type=int)
    job_role   = request.args.get("job_role")
    difficulty = request.args.get("difficulty")
    category   = request.args.get("category")

    result = PracticeService.list_questions(
        page=page,
        per_page=per_page,
        job_role=job_role,
        difficulty=difficulty,
        category=category,
    )
    return jsonify(result), 200


# ── GET /api/practice/<id> ────────────────────────────────────────────────
@practice_bp.get("/<uuid:question_id>")
@require_role("candidate", "admin", "recruiter", "interviewer")
def get_question(question_id):
    """Get a single practice question."""
    result = PracticeService.get(str(question_id))
    return jsonify(result), 200


# ── POST /api/practice ───────────────────────────────────────────────────
@practice_bp.post("/")
@require_role("admin")
def create_question():
    """Create a new practice question (admin only)."""
    data = PracticeQuestionCreateSchema().load(request.get_json(silent=True) or {})
    result = PracticeService.create(data)
    return jsonify(result), 201


# ── POST /api/practice/seed ──────────────────────────────────────────────
@practice_bp.post("/seed")
@require_role("admin")
def seed_questions():
    """Seed the practice question bank with initial data (admin only)."""
    result = PracticeService.seed()
    return jsonify(result), 200

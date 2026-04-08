"""
Blueprint: /api/scheduling
"""

from datetime import datetime

from flask import request, jsonify

from app.scheduling import scheduling_bp
from app.auth.decorators import require_role, get_current_user
from app.services.scheduling_service import SchedulingService
from app.schemas.availability_schema import AvailabilitySlotSchema, SlotQuerySchema

_slot_schema  = AvailabilitySlotSchema()
_query_schema = SlotQuerySchema()


# ── POST /api/scheduling/slots ────────────────────────────────────────────────
@scheduling_bp.post("/slots")
@require_role("interviewer")
def add_slot():
    body   = request.get_json(silent=True) or {}
    errors = _slot_schema.validate(body)
    if errors:
        return jsonify({"errors": errors}), 422

    data         = _slot_schema.load(body)
    current_user = get_current_user()
    result       = SchedulingService.add_slot(data, str(current_user.id))
    return jsonify(result), 201


# ── DELETE /api/scheduling/slots/<id> ────────────────────────────────────────
@scheduling_bp.delete("/slots/<uuid:slot_id>")
@require_role("interviewer")
def delete_slot(slot_id):
    current_user = get_current_user()
    SchedulingService.delete_slot(str(slot_id), str(current_user.id))
    return jsonify({"message": "Slot deleted"}), 200


# ── GET /api/scheduling/slots ─────────────────────────────────────────────────
@scheduling_bp.get("/slots")
@require_role("admin", "recruiter", "interviewer")
def list_slots():
    errors = _query_schema.validate(request.args)
    if errors:
        return jsonify({"errors": errors}), 422

    params         = _query_schema.load(request.args)
    interviewer_id = params.get("interviewer_id")

    # Interviewers only see their own slots
    current_user = get_current_user()
    if current_user.role.value == "interviewer":
        from app.models.interviewer import Interviewer
        iv = Interviewer.query.filter_by(user_id=current_user.id).first()
        if iv:
            interviewer_id = str(iv.id)

    from_date = None
    to_date   = None
    if params.get("from_date"):
        from_date = datetime.combine(params["from_date"], datetime.min.time())
    if params.get("to_date"):
        to_date = datetime.combine(params["to_date"], datetime.max.time())

    result = SchedulingService.list_slots(
        interviewer_id=interviewer_id,
        from_date=from_date,
        to_date=to_date,
        available_only=params.get("available_only", True),
        page=params.get("page", 1),
        per_page=params.get("per_page", 20),
    )
    return jsonify(result), 200


# ── GET /api/scheduling/match ─────────────────────────────────────────────────
@scheduling_bp.get("/match")
@require_role("admin", "recruiter")
def match_interviewers():
    """Find available interviewers for a given time + tech stack."""
    tech_stack_raw = request.args.get("tech_stack", "")
    tech_stack     = [t.strip() for t in tech_stack_raw.split(",") if t.strip()]
    requested_at_raw = request.args.get("requested_at")
    duration_mins    = request.args.get("duration_mins", 60, type=int)

    if not requested_at_raw:
        return jsonify({"error": "requested_at is required (ISO 8601)"}), 422

    try:
        requested_at = datetime.fromisoformat(requested_at_raw)
    except ValueError:
        return jsonify({"error": "Invalid requested_at format. Use ISO 8601."}), 422

    result = SchedulingService.find_available_interviewers(
        tech_stack=tech_stack,
        requested_at=requested_at,
        duration_mins=duration_mins,
    )
    return jsonify(result), 200

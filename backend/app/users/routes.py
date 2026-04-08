"""
Blueprint: /api/users
"""

from flask import request, jsonify
from flask_jwt_extended import jwt_required

from app.users import users_bp
from app.auth.decorators import require_role, get_current_user
from app.models.user import User
from app.models.candidate import Candidate
from app.models.interviewer import Interviewer
from app.schemas.user_schema import UserSchema, UserUpdateSchema
from app import db

_user_schema        = UserSchema()
_user_schema_list   = UserSchema(many=True)
_update_schema      = UserUpdateSchema()


# ── GET /api/users/me ─────────────────────────────────────────────────────────
@users_bp.get("/me")
@jwt_required()
def get_me():
    user = get_current_user()
    return jsonify(_user_schema.dump(user)), 200


# ── PATCH /api/users/me ───────────────────────────────────────────────────────
@users_bp.patch("/me")
@jwt_required()
def update_me():
    user = get_current_user()
    body = request.get_json(silent=True) or {}

    errors = _update_schema.validate(body)
    if errors:
        return jsonify({"errors": errors}), 422

    data = _update_schema.load(body)
    for field, value in data.items():
        setattr(user, field, value)

    db.session.commit()
    return jsonify(_user_schema.dump(user)), 200


# ── GET /api/users (admin only) ───────────────────────────────────────────────
@users_bp.get("/")
@require_role("admin")
def list_users():
    page     = request.args.get("page", 1, type=int)
    per_page = request.args.get("per_page", 20, type=int)
    role     = request.args.get("role")

    q = User.query
    if role:
        q = q.filter_by(role=role)

    pagination = q.order_by(User.created_at.desc()).paginate(
        page=page, per_page=min(per_page, 100), error_out=False
    )
    return jsonify({
        "items":   _user_schema_list.dump(pagination.items),
        "total":   pagination.total,
        "page":    page,
        "pages":   pagination.pages,
        "per_page": per_page,
    }), 200


# ── GET /api/users/<id> (admin only) ──────────────────────────────────────────
@users_bp.get("/<uuid:user_id>")
@require_role("admin")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify(_user_schema.dump(user)), 200


# ── PATCH /api/users/<id>/deactivate (admin only) ─────────────────────────────
@users_bp.patch("/<uuid:user_id>/deactivate")
@require_role("admin")
def deactivate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = False
    db.session.commit()
    return jsonify({"message": "User deactivated"}), 200


# ── PATCH /api/users/<id>/activate (admin only) ──────────────────────────────
@users_bp.patch("/<uuid:user_id>/activate")
@require_role("admin")
def activate_user(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = True
    db.session.commit()
    return jsonify({"message": "User activated"}), 200


# ── GET /api/users/interviewers ───────────────────────────────────────────────
@users_bp.get("/interviewers")
@require_role("admin", "recruiter")
def list_interviewers():
    approved_only = request.args.get("approved_only", "true").lower() == "true"
    q = Interviewer.query
    if approved_only:
        q = q.filter_by(is_approved=True, is_available=True)

    interviewers = q.all()
    result = []
    for iv in interviewers:
        result.append({
            "id":               str(iv.id),
            "user_id":          str(iv.user_id),
            "full_name":        iv.user.full_name,
            "domains":          iv.domains,
            "tech_stack":       iv.tech_stack,
            "years_of_exp":     iv.years_of_exp,
            "avg_rating":       float(iv.avg_rating) if iv.avg_rating else None,
            "total_interviews": iv.total_interviews,
            "is_available":     iv.is_available,
        })
    return jsonify(result), 200


# ── PATCH /api/users/interviewers/<id>/approve (admin) ───────────────────────
@users_bp.patch("/interviewers/<uuid:interviewer_id>/approve")
@require_role("admin")
def approve_interviewer(interviewer_id):
    interviewer = Interviewer.query.get_or_404(interviewer_id)
    interviewer.is_approved = True
    db.session.commit()
    return jsonify({"message": "Interviewer approved"}), 200

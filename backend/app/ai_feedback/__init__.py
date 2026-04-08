from flask import Blueprint

ai_feedback_bp = Blueprint("ai_feedback", __name__)

from app.ai_feedback import routes  # noqa: F401, E402

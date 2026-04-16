from flask import Blueprint

practice_bp = Blueprint("practice", __name__)

from app.practice import routes  # noqa: F401, E402

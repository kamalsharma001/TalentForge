from flask import Blueprint

scheduling_bp = Blueprint("scheduling", __name__)

from app.scheduling import routes  # noqa: F401, E402

from flask import Blueprint

mock_interviews_bp = Blueprint("mock_interviews", __name__)

from app.mock_interviews import routes  # noqa: F401, E402

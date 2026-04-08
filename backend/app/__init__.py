"""
Application factory.
All extensions are initialised here; blueprints are registered here.
Nothing imports from this module at the top level — only create_app() is
called by run.py and gunicorn.
"""

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_jwt_extended import JWTManager
from flask_cors import CORS

from app.config import get_config

# ── Extension singletons (imported by models, services, etc.) ─────────────────
db = SQLAlchemy()
migrate = Migrate()
jwt = JWTManager()


def create_app(config_class=None) -> Flask:
    app = Flask(__name__)

    # ── Config ────────────────────────────────────────────────────────────────
    cfg = config_class or get_config()
    app.config.from_object(cfg)

    # ── Extensions ────────────────────────────────────────────────────────────
    db.init_app(app)
    migrate.init_app(app, db)
    jwt.init_app(app)

    CORS(
        app,
        origins=[app.config["FRONTEND_URL"]],
        supports_credentials=True,
        allow_headers=["Content-Type", "Authorization"],
        methods=["GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS"],
    )

    # ── Cloudinary global config ───────────────────────────────────────────────
    import cloudinary
    cloudinary.config(
        cloud_name=app.config["CLOUDINARY_CLOUD_NAME"],
        api_key=app.config["CLOUDINARY_API_KEY"],
        api_secret=app.config["CLOUDINARY_API_SECRET"],
        secure=True,
    )

    # ── Import models so Alembic can detect them ──────────────────────────────
    from app.models import (  # noqa: F401
        user, organization, org_member, candidate, resume,
        interviewer, interview, interview_score,
        interview_report, availability_slot, notification,
    )

    # ── Blueprints ────────────────────────────────────────────────────────────
    from app.auth.routes import auth_bp
    from app.users.routes import users_bp
    from app.interviews.routes import interviews_bp
    from app.scheduling.routes import scheduling_bp
    from app.reports.routes import reports_bp
    from app.notifications.routes import notifications_bp
    from app.ai_feedback.routes import ai_feedback_bp

    app.register_blueprint(auth_bp,          url_prefix="/api/auth")
    app.register_blueprint(users_bp,         url_prefix="/api/users")
    app.register_blueprint(interviews_bp,    url_prefix="/api/interviews")
    app.register_blueprint(scheduling_bp,    url_prefix="/api/scheduling")
    app.register_blueprint(reports_bp,       url_prefix="/api/reports")
    app.register_blueprint(notifications_bp, url_prefix="/api/notifications")
    app.register_blueprint(ai_feedback_bp,   url_prefix="/api/feedback")

    # ── Global error handlers ─────────────────────────────────────────────────
    from app.utils.errors import register_error_handlers
    register_error_handlers(app)

    # ── Health-check endpoint ─────────────────────────────────────────────────
    @app.get("/api/health")
    def health():
        return {"status": "ok", "service": "TalentForge API"}

    return app

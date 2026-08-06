from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import cloudinary
from app.config import get_config
from app.utils.errors import register_error_handlers
from app.routers import (
    auth,
    users,
    interviews,
    scheduling,
    reports,
    notifications,
    ai_feedback,
    mock_interviews,
    practice,
)

def create_app(config_class=None) -> FastAPI:
    app = FastAPI(title="TalentForge API")
    cfg = config_class or get_config()
    app.state.config = cfg

    # Configure CORS
    app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "https://talentforge-platform.vercel.app",
    ],
    allow_credentials=True,
    allow_methods=[
        "GET",
        "POST",
        "PUT",
        "PATCH",
        "DELETE",
        "OPTIONS",
    ],
    allow_headers=["Content-Type", "Authorization"],
    )

    # Cloudinary Config
    cloudinary.config(
        cloud_name=cfg.CLOUDINARY_CLOUD_NAME,
        api_key=cfg.CLOUDINARY_API_KEY,
        api_secret=cfg.CLOUDINARY_API_SECRET,
        secure=True,
    )

    # Register Routers
    app.include_router(auth.router)
    app.include_router(users.router)
    app.include_router(interviews.router)
    app.include_router(scheduling.router)
    app.include_router(reports.router)
    app.include_router(notifications.router)
    app.include_router(ai_feedback.router)
    app.include_router(mock_interviews.router)
    app.include_router(practice.router)

    # Health Check Endpoint
    @app.get("/health")
    def health_check():
        return {"status": "healthy", "service": "TalentForge API"}

    # Register global exception handlers
    register_error_handlers(app)

    # Import models so Alembic can find metadata
    from app.models import (
        user, organization, org_member, candidate, resume,
        interviewer, interview, interview_score,
        interview_report, availability_slot, notification,
        mock_interview, practice_question,
    )

    return app

app = create_app()

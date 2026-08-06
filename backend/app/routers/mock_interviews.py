from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.schemas.mock_interview_schema import MockInterviewCreateRequest, MockInterviewSubmitRequest
from app.services.mock_interview_service import MockInterviewService
from app.services.ai_feedback_service import AiFeedbackService

router = APIRouter(prefix="/api/mock-interviews", tags=["mock-interviews"])

@router.post("/", status_code=201)
def create(
    body: MockInterviewCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """Start a new mock interview session."""
    result = MockInterviewService.create(db, str(current_user.id), body.model_dump())
    return result

@router.get("/")
def list_sessions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """List mock interview sessions for the current candidate."""
    result = MockInterviewService.list_for_candidate(db, str(current_user.id), page, per_page)
    return result

@router.get("/{session_id}")
def get_session(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """Get a single mock interview session."""
    result = MockInterviewService.get(db, str(session_id), str(current_user.id))
    return result

@router.post("/{session_id}/submit")
def submit(
    session_id: UUID,
    body: MockInterviewSubmitRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """Submit a candidate's answer for a mock interview session."""
    result = MockInterviewService.submit_answer(
        db, str(session_id), str(current_user.id), body.answer_text
    )
    return result

@router.post("/{session_id}/feedback")
def generate_feedback(
    session_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["candidate"])),
):
    """Generate AI feedback for a completed mock interview session."""
    # Verify ownership first
    MockInterviewService.get(db, str(session_id), str(current_user.id))

    ai_data = AiFeedbackService.generate_mock_feedback(db, str(session_id))
    return {
        "message":    "AI feedback generated",
        "summary":    ai_data.get("summary"),
        "strengths":  ai_data.get("strengths"),
        "weaknesses": ai_data.get("weaknesses"),
        "score":      ai_data.get("score"),
    }

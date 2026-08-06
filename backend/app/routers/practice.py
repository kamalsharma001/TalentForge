from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.database import get_db
from app.dependencies import RoleChecker
from app.schemas.practice_schema import PracticeQuestionCreateRequest
from app.services.practice_service import PracticeService

router = APIRouter(prefix="/api/practice", tags=["practice"])

@router.get("/")
def list_questions(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    job_role: Optional[str] = None,
    difficulty: Optional[str] = None,
    category: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["candidate", "admin", "recruiter", "interviewer"])),
):
    """List practice questions with optional filters."""
    result = PracticeService.list_questions(
        db,
        page=page,
        per_page=per_page,
        job_role=job_role,
        difficulty=difficulty,
        category=category,
    )
    return result

@router.get("/{question_id}")
def get_question(
    question_id: UUID,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["candidate", "admin", "recruiter", "interviewer"])),
):
    """Get a single practice question."""
    result = PracticeService.get(db, str(question_id))
    return result

@router.post("/", status_code=201)
def create_question(
    body: PracticeQuestionCreateRequest,
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["admin"])),
):
    """Create a new practice question (admin only)."""
    result = PracticeService.create(db, body.model_dump())
    return result

@router.post("/seed")
def seed_questions(
    db: Session = Depends(get_db),
    current_user = Depends(RoleChecker(["admin"])),
):
    """Seed the practice question bank with initial data (admin only)."""
    result = PracticeService.seed(db)
    return result

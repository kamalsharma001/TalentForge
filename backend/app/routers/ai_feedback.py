from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.interview import Interview
from app.services.ai_feedback_service import AiFeedbackService
from app.services.report_service import ReportService

router = APIRouter(prefix="/api/feedback", tags=["feedback"])

@router.post("/{interview_id}/generate")
def generate(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter", "interviewer"])),
):
    """
    Generate (or regenerate) AI feedback for a completed interview.
    Persists the result onto the associated InterviewReport.
    """
    ai_data = AiFeedbackService.generate(db, str(interview_id))
    interview = db.get(Interview, interview_id)

    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    # Create report automatically if it does not exist
    if not interview.report:
        ReportService.create(db, str(interview.id), {}, str(current_user.id))
        db.refresh(interview)

    ReportService.attach_ai_summary(db, str(interview.report.id), ai_data)

    return {
        "message": "AI feedback generated",
        "summary":    ai_data.get("summary"),
        "strengths":  ai_data.get("strengths"),
        "weaknesses": ai_data.get("weaknesses"),
    }

@router.get("/{interview_id}/preview")
def preview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter", "interviewer"])),
):
    """
    Return the AI-generated content already stored on the report
    without triggering a new generation.
    """
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    report = interview.report
    if not report or not report.ai_summary:
        raise HTTPException(status_code=404, detail="No AI feedback found. Call /generate first.")

    return {
        "summary": report.ai_summary,
        "strengths": report.ai_strengths,
        "weaknesses": report.ai_weaknesses
    }

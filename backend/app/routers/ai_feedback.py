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

from app.models.interviewer import Interviewer

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
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")

    role = current_user.role.value
    if role == "admin":
        pass
    elif role == "recruiter":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your recruiter account is currently awaiting admin verification. You will be able to create interviews once your account is approved."
            )
        if str(interview.requested_by_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
    elif role == "interviewer":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your interviewer account is currently awaiting admin verification. You will be able to provide availability once your account is approved."
            )
        iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
        if not iv or str(interview.interviewer_id) != str(iv.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
    else:
        raise HTTPException(status_code=403, detail="Forbidden.")

    ai_data = AiFeedbackService.generate(db, str(interview_id))

    # Create report automatically if it does not exist
    if not interview.report:
        # Since ReportService.create expects the interviewer's user id, we pass the interviewer user id of the interview
        # Or if generating as admin/recruiter, we find the interviewer user_id from the database
        interviewer_user_id = str(current_user.id)
        if role != "interviewer" and interview.interviewer:
            interviewer_user_id = str(interview.interviewer.user_id)
        ReportService.create(db, str(interview.id), {}, interviewer_user_id)
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

    role = current_user.role.value
    if role == "admin":
        pass
    elif role == "recruiter":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your recruiter account is currently awaiting admin verification. You will be able to create interviews once your account is approved."
            )
        if str(interview.requested_by_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
    elif role == "interviewer":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your interviewer account is currently awaiting admin verification. You will be able to provide availability once your account is approved."
            )
        iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
        if not iv or str(interview.interviewer_id) != str(iv.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
    else:
        raise HTTPException(status_code=403, detail="Forbidden.")

    report = interview.report
    if not report or not report.ai_summary:
        raise HTTPException(status_code=404, detail="No AI feedback found. Call /generate first.")

    return {
        "summary": report.ai_summary,
        "strengths": report.ai_strengths,
        "weaknesses": report.ai_weaknesses
    }

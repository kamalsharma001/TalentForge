from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.interview import Interview
from app.models.interview_report import InterviewReport
from app.schemas.report_schema import ReportCreateRequest, ReportUpdateRequest
from app.services.report_service import ReportService
from app.services.notification_service import NotificationService
from app.services.ai_feedback_service import AiFeedbackService

router = APIRouter(prefix="/api/reports", tags=["reports"])

from app.models.interviewer import Interviewer
from app.models.candidate import Candidate

@router.post("/{interview_id}", status_code=201)
def create_report(
    interview_id: UUID,
    body: ReportCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["interviewer"])),
):
    if current_user.approval_status != "APPROVED":
        raise HTTPException(
            status_code=403,
            detail="Your interviewer account is currently awaiting admin verification. You will be able to provide availability once your account is approved."
        )
        
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
    if not iv or str(interview.interviewer_id) != str(iv.id):
        raise HTTPException(status_code=403, detail="Forbidden. You are not assigned to this interview.")
        
    result = ReportService.create(db, str(interview_id), body.model_dump(), str(current_user.id))
    return result

@router.get("/{interview_id}")
def get_report(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
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
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this report.")
    elif role == "interviewer":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your interviewer account is currently awaiting admin verification. You will be able to provide availability once your account is approved."
            )
        iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
        if not iv or str(interview.interviewer_id) != str(iv.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this report.")
    elif role == "candidate":
        c = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not c or str(interview.candidate_id) != str(c.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this report.")
    else:
        raise HTTPException(status_code=403, detail="Forbidden.")

    as_candidate = (role == "candidate")
    result = ReportService.get_by_interview(db, str(interview_id), as_candidate=as_candidate)
    return result

@router.patch("/{report_id}/edit")
def update_report(
    report_id: UUID,
    body: ReportUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["interviewer", "admin"])),
):
    report = db.get(InterviewReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    role = current_user.role.value
    if role == "admin":
        pass
    elif role == "interviewer":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your interviewer account is currently awaiting admin verification. You will be able to provide availability once your account is approved."
            )
        iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
        if not iv or str(report.interview.interviewer_id) != str(iv.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this report.")
            
    result = ReportService.update(db, str(report_id), body.model_dump(exclude_unset=True), str(current_user.id))
    return result

@router.post("/{report_id}/publish")
def publish_report(
    report_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter"])),
):
    report = db.get(InterviewReport, report_id)
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
        
    interview = db.get(Interview, report.interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Associated interview not found")
        
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
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this report.")

    result = ReportService.publish(db, str(report_id))

    # Notify the candidate
    if report:
        if interview:
            NotificationService.report_published(db, interview)
    return result

@router.post("/{interview_id}/generate-ai")
def generate_ai_feedback(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter", "interviewer"])),
):
    """
    Trigger AI feedback generation for an interview.
    Attaches the result to the existing report (or creates fields for later).
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

    ai_data = AiFeedbackService.generate(db, str(interview_id))

    # Attach to existing report if one exists
    if interview and interview.report:
        ReportService.attach_ai_summary(db, str(interview.report.id), ai_data)

    return {
        "message":   "AI feedback generated successfully",
        "ai_data":   ai_data,
    }

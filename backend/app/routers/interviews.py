from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.interviewer import Interviewer
from app.models.candidate import Candidate
from app.models.interview import Interview
from app.schemas.interview_schema import (
    InterviewCreateRequest,
    InterviewUpdateRequest,
    InterviewAssignRequest,
    InterviewCompleteRequest,
    InterviewResponse,
)
from app.services.interview_service import InterviewService
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/interviews", tags=["interviews"])

@router.post("/", status_code=201)
def create_interview(
    body: InterviewCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter"])),
):
    if current_user.role.value == "recruiter":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your recruiter account is currently awaiting admin verification. You will be able to create interviews once your account is approved."
            )
            
    result = InterviewService.create(db, body.model_dump(), str(current_user.id))
    return result

@router.get("/")
def list_interviews(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    organization_id: Optional[UUID] = None,
    candidate_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kwargs = {"page": page, "per_page": per_page, "status": status}
    role = current_user.role.value

    if role == "recruiter":
        kwargs["requested_by_id"] = str(current_user.id)
        if candidate_id:
            kwargs["candidate_id"] = str(candidate_id)
    elif role == "interviewer":
        iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
        if iv:
            kwargs["interviewer_id"] = str(iv.id)
        else:
            kwargs["interviewer_id"] = "00000000-0000-0000-0000-000000000000"
    elif role == "candidate":
        c = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if c:
            kwargs["candidate_id"] = str(c.id)
        else:
            kwargs["candidate_id"] = "00000000-0000-0000-0000-000000000000"
    elif role == "admin":
        if organization_id:
            kwargs["organization_id"] = str(organization_id)
        if candidate_id:
            kwargs["candidate_id"] = str(candidate_id)

    result = InterviewService.list_interviews(db, **kwargs)
    return result

@router.get("/{interview_id}")
def get_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    interview_model = db.get(Interview, interview_id)
    if not interview_model:
        raise HTTPException(status_code=404, detail="Interview not found")

    role = current_user.role.value
    if role == "admin":
        pass
    elif role == "recruiter":
        if str(interview_model.requested_by_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
    elif role == "interviewer":
        iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
        if not iv or str(interview_model.interviewer_id) != str(iv.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
    elif role == "candidate":
        c = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if not c or str(interview_model.candidate_id) != str(c.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
    else:
        raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")

    result = InterviewService.get_by_id(db, str(interview_id))
    return result

@router.patch("/{interview_id}")
def update_interview(
    interview_id: UUID,
    body: InterviewUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter"])),
):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    role = current_user.role.value
    if role == "recruiter":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your recruiter account is currently awaiting admin verification. You will be able to create interviews once your account is approved."
            )
        if str(interview.requested_by_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
            
    result = InterviewService.update(
        db,
        str(interview_id),
        body.model_dump(exclude_unset=True),
        str(current_user.id),
    )
    return result

@router.post("/{interview_id}/assign")
def assign_interviewer(
    interview_id: UUID,
    body: InterviewAssignRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter"])),
):
    interview = db.get(Interview, interview_id)
    if not interview:
        raise HTTPException(status_code=404, detail="Interview not found")
        
    role = current_user.role.value
    if role == "recruiter":
        if current_user.approval_status != "APPROVED":
            raise HTTPException(
                status_code=403,
                detail="Your recruiter account is currently awaiting admin verification. You will be able to create interviews once your account is approved."
            )
        if str(interview.requested_by_id) != str(current_user.id):
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")

    result = InterviewService.assign_interviewer(
        db,
        str(interview_id),
        str(body.interviewer_id),
        str(body.slot_id),
    )
    # Trigger notifications
    if interview:
        NotificationService.interview_scheduled(db, interview)
    return result

@router.post("/{interview_id}/complete")
def complete_interview(
    interview_id: UUID,
    body: InterviewCompleteRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["interviewer"])),
):
    if current_user.approval_status != "APPROVED":
        raise HTTPException(
            status_code=403,
            detail="Your interviewer account is currently awaiting admin verification. You will be able to provide availability once your account is approved."
        )
    result = InterviewService.complete(
        db,
        str(interview_id),
        body.model_dump(),
        str(current_user.id),
    )
    return result

@router.post("/{interview_id}/cancel")
def cancel_interview(
    interview_id: UUID,
    body: dict,
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
            raise HTTPException(status_code=403, detail="Forbidden. You do not have access to this interview.")
    else:
        raise HTTPException(status_code=403, detail="Forbidden. Only admin or the requesting recruiter can cancel this interview.")

    reason = body.get("reason")
    result = InterviewService.cancel(db, str(interview_id), reason, str(current_user.id))
    return result

@router.delete("/{interview_id}")
def delete_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    InterviewService.delete_interview(db, str(interview_id))
    return {"message": "Interview deleted successfully"}

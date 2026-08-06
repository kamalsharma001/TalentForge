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
    result = InterviewService.create(db, body.model_dump(), str(current_user.id))
    return result

@router.get("/")
def list_interviews(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    status: Optional[str] = None,
    organization_id: Optional[UUID] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    kwargs = {"page": page, "per_page": per_page, "status": status}
    role = current_user.role.value

    if role == "recruiter":
        kwargs["organization_id"] = str(organization_id) if organization_id else None
    elif role == "interviewer":
        iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
        if iv:
            kwargs["interviewer_id"] = str(iv.id)
    elif role == "candidate":
        c = db.query(Candidate).filter(Candidate.user_id == current_user.id).first()
        if c:
            kwargs["candidate_id"] = str(c.id)

    result = InterviewService.list_interviews(db, **kwargs)
    return result

@router.get("/{interview_id}")
def get_interview(
    interview_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = InterviewService.get_by_id(db, str(interview_id))
    return result

@router.patch("/{interview_id}")
def update_interview(
    interview_id: UUID,
    body: InterviewUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter"])),
):
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
    result = InterviewService.assign_interviewer(
        db,
        str(interview_id),
        str(body.interviewer_id),
        str(body.slot_id),
    )
    # Trigger notifications
    interview = db.get(Interview, interview_id)
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
    reason = body.get("reason")
    result = InterviewService.cancel(db, str(interview_id), reason, str(current_user.id))
    return result

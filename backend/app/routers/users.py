from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User, UserRole
from app.models.candidate import Candidate
from app.models.interviewer import Interviewer
from app.schemas.user_schema import UserResponse, UserUpdateSchema
from app.utils.pagination import paginate_query

router = APIRouter(prefix="/api/users", tags=["users"])

@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user)):
    return current_user

@router.patch("/me", response_model=UserResponse)
def update_me(
    body: UserUpdateSchema,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    data = body.model_dump(exclude_unset=True)
    for field, value in data.items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user

@router.get("/")
def list_users(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    role: Optional[str] = None,
    approval_status: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
    if approval_status:
        query = query.filter(User.approval_status == approval_status)
    query = query.order_by(User.created_at.desc())

    res = paginate_query(query, page, per_page)
    # Serialize items
    items_response = [UserResponse.model_validate(item) for item in res["items"]]
    return {
        "items": items_response,
        "total": res["total"],
        "page": res["page"],
        "pages": res["pages"],
        "per_page": res["per_page"],
    }

@router.get("/interviewers")
def list_interviewers(
    approved_only: bool = Query(True),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter"])),
):
    query = db.query(Interviewer)
    if approved_only:
        query = query.filter(Interviewer.is_approved == True, Interviewer.is_available == True)

    interviewers = query.all()
    result = []
    for iv in interviewers:
        result.append({
            "id":               str(iv.id),
            "user_id":          str(iv.user_id),
            "full_name":        iv.user.full_name,
            "domains":          iv.domains,
            "tech_stack":       iv.tech_stack,
            "years_of_exp":     iv.years_of_exp,
            "avg_rating":       float(iv.avg_rating) if iv.avg_rating else None,
            "total_interviews": iv.total_interviews,
            "is_available":     iv.is_available,
        })
    return result

@router.get("/{user_id}", response_model=UserResponse)
def get_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

@router.patch("/{user_id}/deactivate")
def deactivate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = False
    db.commit()
    return {"message": "User deactivated"}

@router.patch("/{user_id}/activate")
def activate_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.is_active = True
    db.commit()
    return {"message": "User activated"}

@router.patch("/interviewers/{interviewer_id}/approve")
def approve_interviewer(
    interviewer_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    interviewer = db.get(Interviewer, interviewer_id)
    if not interviewer:
        raise HTTPException(status_code=404, detail="Interviewer not found")
    interviewer.is_approved = True
    # Keep User.approval_status synchronized
    if interviewer.user:
        interviewer.user.approval_status = "APPROVED"
    db.commit()
    return {"message": "Interviewer approved"}

@router.patch("/{user_id}/approve")
def approve_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.approval_status = "APPROVED"
    if user.role == UserRole.interviewer:
        iv = db.query(Interviewer).filter(Interviewer.user_id == user.id).first()
        if iv:
            iv.is_approved = True
    db.commit()
    return {"message": "User approved successfully"}

@router.patch("/{user_id}/reject")
def reject_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.approval_status = "REJECTED"
    if user.role == UserRole.interviewer:
        iv = db.query(Interviewer).filter(Interviewer.user_id == user.id).first()
        if iv:
            iv.is_approved = False
    db.commit()
    return {"message": "User rejected successfully"}

@router.delete("/{user_id}")
def delete_user(
    user_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    user = db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
        
    if user.role == UserRole.candidate and user.candidate_profile:
        from app.models.interview import Interview
        from app.models.availability_slot import AvailabilitySlot
        interviews = db.query(Interview).filter(Interview.candidate_id == user.candidate_profile.id).all()
        for interview in interviews:
            db.query(AvailabilitySlot).filter(AvailabilitySlot.interview_id == interview.id).update(
                {AvailabilitySlot.interview_id: None, AvailabilitySlot.is_booked: False},
                synchronize_session=False
            )
            db.delete(interview)

    elif user.role == UserRole.interviewer and user.interviewer_profile:
        from app.models.interview import Interview, InterviewStatus
        from app.models.availability_slot import AvailabilitySlot
        interviews = db.query(Interview).filter(
            Interview.interviewer_id == user.interviewer_profile.id,
            Interview.status == InterviewStatus.scheduled
        ).all()
        for interview in interviews:
            db.query(AvailabilitySlot).filter(AvailabilitySlot.interview_id == interview.id).update(
                {AvailabilitySlot.interview_id: None, AvailabilitySlot.is_booked: False},
                synchronize_session=False
            )
            interview.status = InterviewStatus.cancelled
            interview.cancellation_reason = "Assigned interviewer was deleted from the platform."
            interview.interviewer_id = None

    db.delete(user)
    db.commit()
    return {"message": "User deleted successfully"}

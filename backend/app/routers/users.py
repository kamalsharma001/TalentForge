from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from typing import List, Optional
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
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
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin"])),
):
    query = db.query(User)
    if role:
        query = query.filter(User.role == role)
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
    db.commit()
    return {"message": "Interviewer approved"}

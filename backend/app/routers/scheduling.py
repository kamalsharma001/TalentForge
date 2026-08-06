from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from datetime import datetime, date
from typing import Optional, List
from app.database import get_db
from app.dependencies import get_current_user, RoleChecker
from app.models.user import User
from app.models.interviewer import Interviewer
from app.schemas.availability_schema import AvailabilitySlotCreateRequest
from app.services.scheduling_service import SchedulingService

router = APIRouter(prefix="/api/scheduling", tags=["scheduling"])

@router.post("/slots", status_code=201)
def add_slot(
    body: AvailabilitySlotCreateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["interviewer"])),
):
    result = SchedulingService.add_slot(db, body.model_dump(), str(current_user.id))
    return result

@router.delete("/slots/{slot_id}")
def delete_slot(
    slot_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["interviewer"])),
):
    SchedulingService.delete_slot(db, str(slot_id), str(current_user.id))
    return {"message": "Slot deleted"}

@router.get("/slots")
def list_slots(
    interviewer_id: Optional[UUID] = None,
    from_date: Optional[date] = None,
    to_date: Optional[date] = None,
    available_only: bool = Query(True),
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter", "interviewer"])),
):
    target_interviewer_id = str(interviewer_id) if interviewer_id else None

    # Interviewers only see their own slots
    if current_user.role.value == "interviewer":
        iv = db.query(Interviewer).filter(Interviewer.user_id == current_user.id).first()
        if iv:
            target_interviewer_id = str(iv.id)

    parsed_from_date = None
    parsed_to_date = None
    if from_date:
        parsed_from_date = datetime.combine(from_date, datetime.min.time())
    if to_date:
        parsed_to_date = datetime.combine(to_date, datetime.max.time())

    result = SchedulingService.list_slots(
        db,
        interviewer_id=target_interviewer_id,
        from_date=parsed_from_date,
        to_date=parsed_to_date,
        available_only=available_only,
        page=page,
        per_page=per_page,
    )
    return result

@router.get("/match")
def match_interviewers(
    tech_stack: Optional[str] = Query(None),
    requested_at: str = Query(...),
    duration_mins: int = Query(60, ge=15, le=240),
    db: Session = Depends(get_db),
    current_user: User = Depends(RoleChecker(["admin", "recruiter"])),
):
    """Find available interviewers for a given time + tech stack."""
    stack_list = []
    if tech_stack:
        stack_list = [t.strip() for t in tech_stack.split(",") if t.strip()]

    try:
        parsed_requested_at = datetime.fromisoformat(requested_at)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="Invalid requested_at format. Use ISO 8601.",
        )

    result = SchedulingService.find_available_interviewers(
        db,
        tech_stack=stack_list,
        requested_at=parsed_requested_at,
        duration_mins=duration_mins,
    )
    return result

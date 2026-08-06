from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session
from uuid import UUID
from app.database import get_db
from app.dependencies import get_current_user
from app.models.user import User
from app.services.notification_service import NotificationService

router = APIRouter(prefix="/api/notifications", tags=["notifications"])

@router.get("/")
def list_notifications(
    page: int = Query(1, ge=1),
    per_page: int = Query(20, ge=1, le=100),
    unread_only: bool = Query(False),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = NotificationService.list_for_user(
        db,
        str(current_user.id),
        unread_only=unread_only,
        page=page,
        per_page=per_page,
    )
    return result

@router.get("/unread-count")
def unread_count(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    count = NotificationService.unread_count(db, str(current_user.id))
    return {"unread_count": count}

@router.patch("/{notification_id}/read")
def mark_read(
    notification_id: UUID,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    result = NotificationService.mark_read(db, str(notification_id), str(current_user.id))
    return result

@router.post("/mark-all-read")
def mark_all_read(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    updated = NotificationService.mark_all_read(db, str(current_user.id))
    return {"updated": updated, "message": f"{updated} notifications marked as read"}

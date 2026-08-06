from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class NotificationResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    body: str
    type: Optional[str] = None
    action_url: Optional[str] = None
    interview_id: Optional[UUID] = None
    is_read: bool
    read_at: Optional[datetime] = None
    sent_email: bool
    created_at: datetime

    class Config:
        from_attributes = True

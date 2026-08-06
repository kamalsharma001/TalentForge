from pydantic import BaseModel
from uuid import UUID
from datetime import datetime
from typing import Optional

class AvailabilitySlotResponse(BaseModel):
    id: UUID
    interviewer_id: UUID
    start_time: datetime
    end_time: datetime
    timezone: str
    is_booked: bool
    interview_id: Optional[UUID] = None
    is_recurring: bool
    recurrence_rule: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class AvailabilitySlotCreateRequest(BaseModel):
    start_time: datetime
    end_time: datetime
    timezone: str = "UTC"
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None

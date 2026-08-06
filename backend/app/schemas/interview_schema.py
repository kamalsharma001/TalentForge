from pydantic import BaseModel, EmailStr, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional, List

class InterviewScoreResponse(BaseModel):
    id: UUID
    dimension: str
    score: int
    max_score: int
    notes: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class InterviewScoreCreateRequest(BaseModel):
    dimension: str = Field(..., min_length=1, max_length=100)
    score: int = Field(..., ge=1, le=10)
    notes: Optional[str] = None

class InterviewCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=200)
    job_role: Optional[str] = None
    candidate_id: Optional[UUID] = None
    candidate_email: Optional[EmailStr] = None
    organization_id: UUID
    tech_stack: List[str] = Field(default_factory=list)
    difficulty: str = "medium"
    duration_mins: int = Field(60, ge=15, le=240)
    instructions: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    timezone: str = "UTC"

    @field_validator("difficulty")
    @classmethod
    def validate_diff(cls, v):
        if v not in ("easy", "medium", "hard"):
            raise ValueError("difficulty must be easy, medium, or hard")
        return v

class InterviewUpdateRequest(BaseModel):
    title: Optional[str] = Field(None, min_length=2, max_length=200)
    job_role: Optional[str] = None
    tech_stack: Optional[List[str]] = None
    difficulty: Optional[str] = None
    duration_mins: Optional[int] = Field(None, ge=15, le=240)
    instructions: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    timezone: Optional[str] = None
    meeting_link: Optional[str] = None
    status: Optional[str] = None
    cancellation_reason: Optional[str] = None

    @field_validator("difficulty")
    @classmethod
    def validate_diff(cls, v):
        if v is not None and v not in ("easy", "medium", "hard"):
            raise ValueError("difficulty must be easy, medium, or hard")
        return v

class InterviewResponse(BaseModel):
    id: UUID
    title: str
    job_role: Optional[str] = None
    tech_stack: List[str]
    difficulty: str
    duration_mins: int
    instructions: Optional[str] = None
    scheduled_at: Optional[datetime] = None
    timezone: str
    meeting_link: Optional[str] = None
    status: str
    cancellation_reason: Optional[str] = None
    recording_url: Optional[str] = None
    recording_duration_s: Optional[int] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime
    organization_id: UUID
    candidate_id: UUID
    interviewer_id: Optional[UUID] = None
    requested_by_id: Optional[UUID] = None
    scores: List[InterviewScoreResponse] = Field(default_factory=list)

    class Config:
        from_attributes = True

class InterviewAssignRequest(BaseModel):
    interviewer_id: UUID
    slot_id: UUID

class InterviewCompleteRequest(BaseModel):
    recording_url: Optional[str] = None
    recording_cloudinary_id: Optional[str] = None
    recording_duration_s: Optional[int] = None
    scores: List[InterviewScoreCreateRequest] = Field(default_factory=list)

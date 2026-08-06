from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional

class MockInterviewCreateRequest(BaseModel):
    job_role: Optional[str] = None
    difficulty: str = "medium"
    category: str = "behavioral"
    duration_mins: int = Field(30, ge=10, le=120)

    @field_validator("difficulty")
    @classmethod
    def validate_diff(cls, v):
        if v not in ("easy", "medium", "hard"):
            raise ValueError("difficulty must be easy, medium, or hard")
        return v

    @field_validator("category")
    @classmethod
    def validate_cat(cls, v):
        if v not in ("behavioral", "technical", "system_design"):
            raise ValueError("category must be behavioral, technical, or system_design")
        return v

class MockInterviewSubmitRequest(BaseModel):
    answer_text: str = Field(..., min_length=1)

class MockInterviewResponse(BaseModel):
    id: UUID
    candidate_id: UUID
    practice_question_id: Optional[UUID] = None
    job_role: Optional[str] = None
    difficulty: str
    category: str
    question_text: str
    answer_text: Optional[str] = None
    duration_mins: int
    status: str
    ai_summary: Optional[str] = None
    ai_strengths: Optional[str] = None
    ai_weaknesses: Optional[str] = None
    ai_score: Optional[int] = None
    ai_generated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

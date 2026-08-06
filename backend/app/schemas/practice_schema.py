from pydantic import BaseModel, Field, field_validator
from uuid import UUID
from datetime import datetime
from typing import Optional

class PracticeQuestionCreateRequest(BaseModel):
    question: str = Field(..., min_length=5)
    job_role: str = Field(..., min_length=2, max_length=150)
    difficulty: str
    category: str
    hint: Optional[str] = None
    sample_answer: Optional[str] = None

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

class PracticeQuestionResponse(BaseModel):
    id: UUID
    question: str
    job_role: str
    difficulty: str
    category: str
    hint: Optional[str] = None
    sample_answer: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
